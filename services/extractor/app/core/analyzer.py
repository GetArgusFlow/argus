# argus/services/extractor/app/core/analyzer.py

from typing import Dict, Any, List
from loguru import logger
from langdetect import detect
from bs4 import BeautifulSoup
from app.core.context import shared_context
from app.core.dependency_resolver import DependencyResolver
from app.core.types import ExtractionResult, FieldExtractionStatus
from app.core.models import get_product_data_model, _BaseProductData
from app.utils.html_processor import clean_html_for_extraction
from app.utils.shared_resources import get_resources
from app.core.module_loader import discover_and_load_modules
from app.config import settings


class ProductPageAnalyzer:
    """
    Orchestrates the full product page analysis by dynamically discovering modules,
    resolving their dependencies, and executing them in the correct order.
    """

    def __init__(self):
        # 1. Discover all available modules (both Free and Pro) at startup.
        #    This only happens once for efficiency.
        self.free_modules = discover_and_load_modules("app.modules")
        self.pro_modules = self._discover_pro_modules()

        # Determine the status of the service at startup
        self.is_pro_activated = bool(self.pro_modules)

        # Combine all modules to build the complete data model
        all_discovered_modules = self.free_modules | self.pro_modules

        # 2. Now create the data model based on the discovered modules
        self.ProductDataModel = get_product_data_model(all_discovered_modules)

        # 3. The rest of the __init__ remains the same
        self.alias_to_field_map = self._build_alias_map()

        logger.info(
            f"Analyzer initialized with {len(self.free_modules)} free modules discovered."
        )
        if self.is_pro_activated:
            logger.info("Argus Pro package detected. Service is running in PRO mode.")
        else:
            logger.info("Running in FREE mode. Pro features are not available.")

    def _discover_pro_modules(self) -> Dict[str, Any]:
        """Attempts to dynamically discover and load the Pro modules."""
        try:
            # Important: the path must match the structure in your argus-pro repo.
            return discover_and_load_modules("pro.extractor.modules")
        except ImportError:
            # This is normal behavior if the Pro package is not installed.
            return {}

    def _build_alias_map(self) -> Dict[str, str]:
        """Builds the alias map from the settings for data enrichment."""
        return {
            alias.lower(): field
            for field, aliases in settings.field_aliases.items()
            for alias in aliases
        }

    def analyze(self, html_content: str, url: str, use_llm: bool) -> Dict[str, Any]:
        """
        Performs the full analysis for a given user tier.
        """
        tier = "pro" if self.is_pro_activated else "free"
        logger.info(f"Analyzer: Starting analysis for URL: {url} (Tier: {tier})")

        # STEP 1: Assemble the active modules based on the tier.
        active_modules = self.free_modules.copy()
        if tier == "pro" and self.pro_modules:
            logger.info("Pro tier activated, merging Pro modules.")
            active_modules.update(self.pro_modules)

        # STEP 2: Use the DependencyResolver to determine the execution order.
        try:
            resolver = DependencyResolver(active_modules)
            execution_order = resolver.sort()
            logger.info(f"Module execution order resolved: {execution_order}")
        except ValueError as e:
            logger.error(
                f"Module dependency error: {e}. Aborting analysis.", exc_info=True
            )
            raise  # Stop the execution and propagate the error

        # Initialize the data objects for this run
        product_data = self.ProductDataModel()
        shared_context.initialize(
            self._create_initial_context(html_content, url, use_llm)
        )

        # STEP 3: Execute the sorted modules.
        self._run_modules(product_data, execution_order, active_modules)

        # STEP 4: Enrich the data (optional, after the main analysis).

        self._enrich_from_specifications(product_data)

        # STEP 5: Choose the best results from the scoreboard.
        self._resolve_best_results(product_data)

        logger.success("Analyzer: Full analysis completed.")

        # Get the final results dictionary
        final_results = product_data.get_final_results()

        # Create a new dictionary sorted alphabetically by key
        return dict(sorted(final_results.items()))

    def _create_initial_context(
        self, html_content: str, url: str, use_llm: bool
    ) -> Dict[str, Any]:
        """Creates the initial context for an analysis run."""
        # PHASE 1: HTML Preprocessing
        logger.info("Analyzer: PHASE 1: Starting HTML Preprocessing.")
        preprocessed_soup = clean_html_for_extraction(html_content)
        try:
            lang_code = detect(preprocessed_soup.get_text())
        except Exception:
            lang_code = settings.language.default

        return {
            "raw_soup": BeautifulSoup(html_content, "lxml"),
            "preprocessed_soup": preprocessed_soup,
            "current_url": url,
            "resources": get_resources(),
            "lang_code": lang_code,
            "use_llm": use_llm,
            "processed_elements": set(),  # Initialize processed_elements set
        }

    def _run_modules(
        self,
        product_data: _BaseProductData,
        execution_order: List[str],
        active_modules: Dict[str, Any],
    ):
        """Executes all active modules in the correct sorted order."""
        logger.info(f"Analyzer: Running modules in sorted order: {execution_order}")
        for module_name in execution_order:
            module = active_modules.get(module_name)
            if not module:
                logger.warning(
                    f"Module '{module_name}' was in execution order but could not be found."
                )
                continue

            try:
                # Call the 'extract' function of the module
                extracted_data, selector, status, score = module.extract()

                if extracted_data is None:
                    continue

                # Step 1: ALWAYS put the module's primary result on the context
                # This allows 'price' to depend on 'json_ld', etc.
                shared_context.update(module_name, extracted_data)

                # Step 2: Check if this module *is* a field on the data model
                # (e.g., 'price', 'title', 'json_ld', 'open_graph')
                if hasattr(product_data, module_name):
                    # If yes, add its main result to the scoreboard for that field
                    field_name = module_name
                    result = ExtractionResult(
                        value=extracted_data,
                        source=selector,
                        score=score,
                        status=status,
                    )
                    product_data.add_result(field_name, result)

                # Step 3: If the data is a dict, ALSO loop through it
                # to populate sub-fields (like 'title' from 'open_graph')
                if isinstance(extracted_data, dict):
                    for field, value in extracted_data.items():
                        # Check if this sub-key is a field AND it's not the module's own name
                        # (We've already handled the 'open_graph' field itself in Step 2)
                        if (
                            field != module_name
                            and value is not None
                            and hasattr(product_data, field)
                        ):
                            # This adds 'title' and 'image' from the 'open_graph' module
                            result = ExtractionResult(
                                value=value,
                                source=f"{module_name} ({selector})",
                                score=score,
                                status=status,
                            )
                            product_data.add_result(field, result)

            except Exception as e:
                logger.error(
                    f"Error during execution of module '{module_name}': {e}",
                    exc_info=True,
                )

    def _enrich_from_specifications(self, product_data: _BaseProductData):
        """
        Scans the found specifications and adds results to the scoreboard
        for fields that have not yet been found with high confidence.
        """
        logger.info("Enrichment: Checking specifications for extra data...")

        # Get the specifications from the snapshot of this run
        specs_results = product_data.all_results.get("specifications")
        if not specs_results:
            logger.debug("Enrichment: No specifications found to enrich from.")
            return

        # We take the best specification extraction as the source
        best_specs_result = max(specs_results, key=lambda r: r.score)
        specifications = best_specs_result.value

        if not specifications:
            return

        for spec_category in specifications:
            details = spec_category.get("details")
            if isinstance(details, dict):
                for key, value in details.items():
                    key_lower = key.lower().strip()

                    # Check if this specification key is a known alias
                    target_field = self.alias_to_field_map.get(key_lower)

                    if target_field:
                        # We have a match! E.g., "Merk" -> "brand"
                        logger.debug(
                            f"Enrichment: Found potential '{target_field}' field from spec key '{key}' with value '{value}'."
                        )

                        # Add this result to the scoreboard
                        result = ExtractionResult(
                            value=str(value).strip(),
                            source=f"specifications (key: {key})",
                            # Give a solid, but not the highest, score
                            score=150,
                            status=FieldExtractionStatus.FOUND_IN_SPECS,
                        )
                        product_data.add_result(target_field, result)

    def _resolve_best_results(self, product_data: _BaseProductData):
        """
        Iterates over the scoreboard ('all_results') and selects the entry
        with the highest score for each field to set the final value.
        """
        logger.info("Resolving best results from scoreboard...")
        for field_name, results in product_data.all_results.items():
            if results:
                # Find the result with the highest score
                best_result = max(results, key=lambda r: r.score)

                # Set the final value on the model
                if hasattr(product_data, field_name):
                    setattr(product_data, field_name, best_result.value)
                    # Also update the status and selector for the winner
                    product_data.field_status[field_name] = best_result.status
                    product_data.selectors_used[field_name] = best_result.source
                    logger.debug(
                        f"Resolved field '{field_name}': chose value from '{best_result.source}' with score {best_result.score}."
                    )
