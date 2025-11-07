# ArgusProject/argus/services/matcher/app/core/engine.py

import os
import shutil
import random
import argparse
import numpy as np
import faiss
import torch
from itertools import combinations
from tqdm import tqdm
from sentence_transformers import SentenceTransformer, InputExample, losses
from sqlalchemy import create_engine, text, bindparam, Row
from loguru import logger
from typing import List, Dict, Tuple, Optional, Any

from app.config import settings


class MatchingEngine:
    """
    Encapsulates all logic for model training, FAISS indexing, and product searching.
    """

    def __init__(self):
        self.model: Optional[SentenceTransformer] = None
        self.index: Optional[faiss.Index] = None
        self.ids: List[int] = []
        self._append_count: int = 0
        self.db_engine = create_engine(
            settings.mysql_uri, pool_recycle=3600, pool_pre_ping=True
        )

    # Resource Management

    def load_resources(self):
        """Loads the SentenceTransformer model, FAISS index, and ID map into memory."""
        if self.model:
            logger.info("Resources are already loaded.")
            return

        logger.info("Matcher Engine: Loading resources...")
        model_path = (
            settings.finetuned_model_path
            if settings.finetuned_model_path.exists()
            else settings.matcher.base_model_name
        )

        try:
            self.model = SentenceTransformer(
                str(model_path), device=settings.matcher.device
            )
            self.index = faiss.read_index(str(settings.index_path))
            self.ids = list(np.load(settings.id_map_path, allow_pickle=True))
            logger.success(
                f"Matcher Engine: Resources loaded. {self.index.ntotal} vectors in index."
            )
        except Exception as e:
            logger.critical(
                f"Failed to load resources. Run 'make setup' first. Error: {e}"
            )
            raise RuntimeError("Could not load ML resources.") from e

    def clear_resources(self):
        """Clears in-memory resources to allow for a clean reload after training."""
        self.model = None
        self.index = None
        self.ids = []
        logger.info("In-memory resources have been cleared.")

    def _persist_index(self):
        """Saves the current FAISS index and ID map to disk."""
        if not self.index:
            return
        faiss.write_index(self.index, str(settings.index_path))
        np.save(settings.id_map_path, np.array(self.ids))
        logger.info(f"Index and ID map saved to disk ({len(self.ids)} items)")

    # Data Fetching and Preparation

    def _prepare_text_from_row(self, row: Row) -> str:
        """
        Builds the descriptive text string from a database row.
        It expects the row to have the standard columns defined in config.yml.
        """
        if not row:
            return ""

        # Convert row to a dictionary for safe .get() access
        data = dict(row._mapping)
        p = []

        if title := data.get("title"):
            p.append(str(title).strip())
        if brand := data.get("brand"):
            p.append(f"brand: {brand}")
        if (contents := data.get("contents")) and (unit := data.get("unit")):
            p.append(f"{contents} {unit}")
        if pack := data.get("pack"):
            p.append(str(pack))
        if colors := data.get("colors"):
            p.append(f"colors: {colors}")
        if typ := data.get("type"):
            p.append(f"type: {typ}")
        if ean := data.get("ean"):
            p.append(f"ean: {ean}")
        if dim := data.get("dimensions"):
            p.append(f"dimensions: {dim}")

        return " | ".join(p)

    def _fetch_products_by_ids(self, ids: List[int]) -> Dict[int, Row]:
        """
        Fetches the full product data rows for a list of IDs.
        Returns a dictionary mapping product ID to the full SQLAlchemy Row.
        """
        if not ids:
            return {}

        sql = text(settings.database_queries.product_by_id_query).bindparams(
            bindparam("ids", expanding=True)
        )

        with self.db_engine.connect() as conn:
            # The query must return a column aliased as 'id'
            return {r.id: r for r in conn.execute(sql, {"ids": ids})}

    def get_text_for_id(self, product_id: int) -> Optional[str]:
        """Gets the prepared text string for a single product ID."""
        row_map = self._fetch_products_by_ids([product_id])
        if product_id not in row_map:
            return None
        return self._prepare_text_from_row(row_map[product_id])

    def get_data_for_id(self, product_id: int) -> Optional[Dict]:
        """Gets the full product data row as a dictionary for a single product ID."""
        row_map = self._fetch_products_by_ids([product_id])
        if product_id not in row_map:
            return None
        # Convert the SQLAlchemy Row to a standard dictionary
        return dict(row_map[product_id]._mapping)

    def _iter_all_products(self):
        """Iterates through all products in the database for indexing."""
        sql = text(settings.database_queries.indexing_query)
        with self.db_engine.connect() as conn:
            # The query must return a column aliased as 'id' and the other fields
            for row in conn.execute(sql):
                yield row.id, row

    def _is_good_negative(self, a: Dict, b: Dict) -> bool:
        """
        Determines if two product data dictionaries are suitable hard negatives.
        Operates on dictionaries (from get_data_for_id).
        """
        # EANs can be a single value or a string with "|" separators
        ean1 = set(str(a.get("ean") or "").split("|"))
        ean2 = set(str(b.get("ean") or "").split("|"))
        if ean1 and ean2 and ean1 & ean2 and "None" not in ean1:
            return False

        if a.get("type") and b.get("type") and a["type"] != b["type"]:
            return False
        if a.get("contents") == b.get("contents"):
            return False
        if a.get("pack") == b.get("pack"):
            return False
        return True

    # Search and Index Modification

    def _penalty(self, query_data: Dict, cand_data: Dict, base_score: float) -> float:
        """
        Applies penalties to a match score based on attribute mismatches.
        Operates on dictionaries (from get_data_for_id).
        """
        if query_data.get("colors") == cand_data.get("colors"):
            base_score *= 0.9
        if query_data.get("contents") != cand_data.get("contents"):
            base_score *= 0.85
        if query_data.get("brand") != cand_data.get("brand"):
            base_score *= 0.85
        return base_score

    def search(
        self,
        query_text: str,
        k: int,
        query_data: Optional[Dict] = None,
        allowed_store_ids: Optional[List[int]] = None,
    ) -> List[Tuple[int, float]]:
        if not self.model or not self.index:
            raise RuntimeError("Model and index are not loaded.")

        vec = (
            self.model.encode(query_text, convert_to_numpy=True)
            .reshape(1, -1)
            .astype("float32")
        )
        faiss.normalize_L2(vec)

        scores, idxs = self.index.search(vec, k * 10)  # Search wider (eg 10x top_k)
        pids = [int(self.ids[i]) for i in idxs[0] if i >= 0]

        if not pids:
            return []

        products_data: Dict[int, Row] = self._fetch_products_by_ids(pids)

        filtered_matches = []
        for rank, i in enumerate(idxs[0]):
            if i < 0:
                continue
            pid = int(self.ids[i])

            cand_row = products_data.get(pid)
            if not cand_row:
                continue

            if allowed_store_ids:
                try:
                    cand_store_id = cand_row.store_id
                    if cand_store_id not in allowed_store_ids:
                        continue
                except AttributeError:
                    logger.warning(
                        f"Column 'store_id' not found in product_by_id_query for product ID {pid}. Unable to filter on allowed_store_ids."
                    )
                    pass

            cand_data = dict(cand_row._mapping)
            score = float(scores[0][rank])

            if query_data:
                score = self._penalty(query_data, cand_data, score)

            filtered_matches.append(
                (pid, score)
            )  # if you want to see the text, add: self.get_text_for_id(pid)

        filtered_matches.sort(key=lambda x: x[1], reverse=True)
        return filtered_matches[:k]

    def add_product_to_index(self, product_id: int):
        if not self.model or not self.index:
            self.load_resources()
        if product_id in self.ids:
            logger.info(f"PID {product_id} is already in the index. Skipping.")
            return

        txt = self.get_text_for_id(product_id)  # This now uses the new row-based method
        if not txt:
            raise ValueError(
                f"Product {product_id} not found or has no text representation."
            )

        vec = (
            self.model.encode(txt, convert_to_numpy=True)
            .reshape(1, -1)
            .astype("float32")
        )
        faiss.normalize_L2(vec)

        self.index.add(vec)
        self.ids.append(product_id)

        self._append_count += 1
        if self._append_count >= settings.matcher.autosave_every:
            self._persist_index()
            self._append_count = 0

    def delete_product_from_index(self, product_id: int):
        if not self.model or not self.index:
            self.load_resources()
        if product_id not in self.ids:
            raise ValueError(f"Product {product_id} not found in the index.")

        idx_to_remove = self.ids.index(product_id)
        self.ids.pop(idx_to_remove)
        self.index.remove_ids(np.array([idx_to_remove], dtype="int64"))
        self._persist_index()

    def add_test_product(self, product_data: Dict[str, Any]):
        """
        (FOR TESTING) Inserts a product into the DB and then adds it to the index.
        """
        pid = product_data.get("product_id")
        if not pid:
            raise ValueError("product_id is required for add_test_product")

        # 1. Insert into Database
        with self.db_engine.connect() as conn:
            conn.execute(text("BEGIN"))
            try:
                # Insert into products table
                conn.execute(
                    text(
                        """
                    INSERT INTO products (product_id, store_id, title, brand, contents, unit) 
                    VALUES (:product_id, :store_id, :title, :brand, :contents, :unit)
                    """
                    ),
                    product_data,
                )

                # Insert into product_matches (using PID as GID for simplicity)
                conn.execute(
                    text(
                        "INSERT INTO product_matches (group_id, product_id) VALUES (:gid, :pid)"
                    ),
                    {"gid": pid, "pid": pid},
                )
                conn.execute(text("COMMIT"))
                logger.info(f"Test product {pid} inserted into database.")
            except Exception as e:
                conn.execute(text("ROLLBACK"))
                logger.error(f"Failed to insert test product {pid} into DB: {e}")
                raise

        # 2. Add to Index (this will now work)
        self.add_product_to_index(pid)
        logger.info(f"Test product {pid} added to index.")

    def delete_test_product(self, product_id: int):
        """
        (FOR TESTING) Deletes a product from the index and the database.
        """
        # 1. Delete from Index
        try:
            self.delete_product_from_index(product_id)
            logger.info(f"Test product {product_id} deleted from index.")
        except ValueError as e:
            logger.warning(
                f"Test product {product_id} not in index. Deleting from DB only. Error: {e}"
            )

        # 2. Delete from Database
        with self.db_engine.connect() as conn:
            conn.execute(text("BEGIN"))
            try:
                conn.execute(
                    text("DELETE FROM product_matches WHERE product_id = :id"),
                    {"id": product_id},
                )
                conn.execute(
                    text("DELETE FROM products WHERE product_id = :id"),
                    {"id": product_id},
                )
                conn.execute(text("COMMIT"))
                logger.info(f"Test product {product_id} deleted from database.")
            except Exception as e:
                conn.execute(text("ROLLBACK"))
                logger.error(f"Failed to delete test product {product_id} from DB: {e}")
                raise

    # Training Pipeline

    def _fetch_positive_pairs(self) -> List[Tuple[int, int]]:
        sql = text(settings.database_queries.training_pairs_query)
        groups = {}
        with self.db_engine.connect() as conn:
            for gid, sid in conn.execute(sql):  # Expects group_id, product_id
                groups.setdefault(gid, []).append(sid)
        return [pair for g in groups.values() for pair in combinations(sorted(g), 2)]

    def _build_training_examples(
        self, pos_pairs: List[Tuple[int, int]]
    ) -> List[InputExample]:
        logger.info("Building training examples...")
        all_pair_ids = list({i for pair in pos_pairs for i in pair})
        id2data = self._fetch_products_by_ids(all_pair_ids)  # Returns Dict[int, Row]

        pos, neg = [], []
        for a, b in tqdm(pos_pairs, desc="Creating positive examples"):
            if a in id2data and b in id2data:
                ta = self._prepare_text_from_row(id2data[a])
                tb = self._prepare_text_from_row(id2data[b])
                if ta and tb:
                    pos.append(InputExample(texts=[ta, tb], label=1.0))

        items = list(id2data.values())  # This is a list of Rows
        random.seed(42)
        for row1 in tqdm(items, desc="Creating hard negative examples"):
            d1 = dict(row1._mapping)
            for _ in range(20):
                row2 = random.choice(items)
                if row1.id == row2.id:
                    continue

                d2 = dict(row2._mapping)
                if self._is_good_negative(d1, d2):
                    t1 = self._prepare_text_from_row(row1)
                    t2 = self._prepare_text_from_row(row2)
                    if t1 and t2:
                        neg.append(InputExample(texts=[t1, t2], label=0.0))
                    break

        logger.info(f"Train samples: +{len(pos)} positives, -{len(neg)} negatives")
        return pos + neg

    def _finetune_model(
        self, base_model: SentenceTransformer, examples: List[InputExample]
    ) -> SentenceTransformer:
        if not examples:
            logger.warning("No training examples provided. Returning base model.")
            return base_model

        loader = torch.utils.data.DataLoader(
            examples, shuffle=True, batch_size=settings.matcher.batch_size
        )
        loss = losses.CosineSimilarityLoss(base_model)

        logger.info(
            f"Starting model fine-tuning for {settings.matcher.epochs} epochs..."
        )
        base_model.fit(
            [(loader, loss)],
            epochs=settings.matcher.epochs,
            show_progress_bar=True,
            output_path=str(settings.finetuned_model_path),
            warmup_steps=int(len(loader) * settings.matcher.epochs * 0.1),
        )
        logger.success(
            f"Fine-tuning complete. Model saved to {settings.finetuned_model_path}"
        )
        return SentenceTransformer(
            str(settings.finetuned_model_path), device=settings.matcher.device
        )

    def _build_faiss_index(self, model: SentenceTransformer):
        logger.info("Building new FAISS index from all products...")
        vecs, ids = [], []
        os.makedirs(settings.matcher.models_dir, exist_ok=True)

        for pid, row in tqdm(self._iter_all_products(), desc="Encoding all products"):
            txt = self._prepare_text_from_row(row)
            if txt:
                vecs.append(model.encode(txt, convert_to_numpy=True))
                ids.append(pid)

        if not vecs:
            raise RuntimeError(
                "No vectors were generated. Cannot build an empty index."
            )

        mat = np.vstack(vecs).astype("float32")
        faiss.normalize_L2(mat)
        index = faiss.IndexFlatIP(mat.shape[1])
        index.add(mat)

        faiss.write_index(index, str(settings.index_path))
        np.save(settings.id_map_path, np.array(ids))
        logger.success(f"FAISS index built with {len(ids)} vectors.")

    def run_training_pipeline(self, retrain: bool = False):
        """Orchestrates the entire model training and indexing pipeline."""
        logger.info("Starting training pipeline...")
        if retrain:
            logger.warning("RETRAIN flag is set. Deleting old model and index files.")
            if settings.finetuned_model_path.exists():
                shutil.rmtree(settings.finetuned_model_path)
            if settings.index_path.exists():
                os.remove(settings.index_path)
            if settings.id_map_path.exists():
                os.remove(settings.id_map_path)

        pos_pairs = self._fetch_positive_pairs()
        examples = self._build_training_examples(pos_pairs)

        base_model = SentenceTransformer(
            settings.matcher.base_model_name, device=settings.matcher.device
        )
        finetuned_model = self._finetune_model(base_model, examples)

        self._build_faiss_index(finetuned_model)

        logger.success(
            "Training pipeline completed. Forcing a reload of resources in the service."
        )
        self.clear_resources()
        self.load_resources()


# Singleton Instance and Command-Line Interface

engine = MatchingEngine()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train the product matcher model and build the index."
    )
    parser.add_argument(
        "--train",
        action="store_true",
        help="Start the fine-tuning and indexing process.",
    )
    parser.add_argument(
        "--retrain",
        action="store_true",
        help="Delete old artifacts before starting the training process.",
    )
    args = parser.parse_args()

    if args.train or args.retrain:
        # This allows running 'make train' or 'make retrain' from the command line
        cli_engine = MatchingEngine()
        cli_engine.run_training_pipeline(retrain=args.retrain)
    else:
        parser.print_help()
