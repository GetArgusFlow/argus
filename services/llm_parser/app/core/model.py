# app/core/model.py

import json
from llama_cpp import Llama, LlamaGrammar
from loguru import logger
import os

from app.config import settings
from app.core.prompt import PROMPT_TEMPLATE


def load_model() -> tuple[Llama, LlamaGrammar]:
    """
    Load and return llm and grammar. This is called only once at startup.
    """
    try:
        grammar_path = settings.grammar_path
        if not os.path.exists(grammar_path):
            raise FileNotFoundError(
                f"Grammar file not found at {grammar_path}. Run 'make generate-grammar'."
            )
        logger.info(f"Loading grammar from: {grammar_path}")
        grammar = LlamaGrammar.from_file(grammar_path)

        model_path = settings.model_path
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model file not found at {model_path}. Run 'make download-model'."
            )
        logger.info(f"Loading model from: {model_path}")

        llm = Llama(
            model_path=str(model_path),
            n_ctx=settings.llm.params.n_ctx,
            n_gpu_layers=settings.llm.params.n_gpu_layers,
            verbose=False,
        )
        logger.success("Model and grammar prepared successfully.")
        return llm, grammar

    except Exception as e:
        logger.critical(
            f"FATAL ERROR: Could not load model or grammar. Error: {e}", exc_info=True
        )
        raise e


def run_inference(html_snippet: str, llm: Llama, grammar: LlamaGrammar) -> dict:
    final_prompt = PROMPT_TEMPLATE.format(html_snippet=html_snippet)

    logger.debug("Running inference with LLM...")
    output = llm(
        final_prompt,
        max_tokens=settings.llm.params.max_tokens,
        temperature=settings.llm.params.temperature,
        grammar=grammar,
        stream=False,
    )

    json_string = output["choices"][0]["text"]  # type: ignore
    logger.debug(f"Raw LLM output: {json_string}")

    return json.loads(json_string)
