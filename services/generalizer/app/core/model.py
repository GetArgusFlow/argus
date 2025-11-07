# argus/services/generalizer/app/core/model.py

import json
import os
import importlib
import yaml
from pathlib import Path
from llama_cpp import Llama, LlamaGrammar
from loguru import logger
from typing import Dict, Any, Callable

from app.config import settings
from app.core.prompt_builder import PromptBuilder

# Cache for prompt builders (holds PromptBuilder instances)
prompt_builder_cache: Dict[str, PromptBuilder] = {}
# Cache for grammars (holds LlamaGrammar instances)
grammar_cache: Dict[str, LlamaGrammar] = {}

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def get_prompt_builder(language: str) -> Callable[[str], str]:
    """
    Dynamically loads language data, instantiates a PromptBuilder,
    and returns its 'create_full_prompt' method.
    """
    if language in prompt_builder_cache:
        return prompt_builder_cache[language].create_full_prompt

    try:
        lang_dir = PROMPTS_DIR / language
        if not lang_dir.exists():
            raise FileNotFoundError(f"Language directory not found: {lang_dir}")

        # 1. Load language-specific examples
        examples_module_name = f"app.prompts.{language}.examples"
        examples_module = importlib.import_module(examples_module_name)
        json_examples = getattr(examples_module, "json_examples")

        # 2. Load language-specific prompt content
        content_module_name = f"app.prompts.{language}.prompt"
        content_module = importlib.import_module(content_module_name)
        system_prompt = getattr(content_module, "SYSTEM_PROMPT_CONTENT")
        user_prefix = getattr(content_module, "USER_PROMPT_PREFIX")

        # 3. Load language-specific categories
        categories_file = lang_dir / "categories.yml"
        if not categories_file.exists():
            raise FileNotFoundError(f"Missing categories.yml for language '{language}'")
        with open(categories_file, "r", encoding="utf-8") as f:
            categories_list = yaml.safe_load(f)

        # 4. Create and cache the builder instance
        builder = PromptBuilder(
            system_prompt_template=system_prompt,
            examples=json_examples,
            user_prefix=user_prefix,
            categories_list=categories_list,
        )
        prompt_builder_cache[language] = builder

        logger.info(
            f"Successfully loaded and cached prompt builder for language: '{language}'"
        )
        return builder.create_full_prompt

    except ImportError as e:
        logger.error(f"Data module not found for language: '{language}'. {e}")
        raise ValueError(f"Unsupported language: '{language}'")
    except (FileNotFoundError, AttributeError) as e:
        logger.error(f"Missing required data file for '{language}': {e}")
        raise ValueError(f"Configuration error for language '{language}'.")
    except Exception as e:
        logger.error(f"Failed to load prompt builder for '{language}': {e}")
        raise ValueError(f"Could not load resources for language '{language}'.")


def get_language_grammar(language: str) -> LlamaGrammar:
    """
    Dynamically loads and caches the GBNF grammar for a given language.
    """
    if language in grammar_cache:
        return grammar_cache[language]

    try:
        grammar_file = PROMPTS_DIR / language / "grammar.gbnf"
        if not grammar_file.exists():
            logger.error(f"Missing grammar.gbnf for language '{language}'.")
            logger.error("Run 'make generate-grammars' to create it.")
            raise FileNotFoundError(f"Missing grammar file for '{language}'")

        grammar = LlamaGrammar.from_file(str(grammar_file))
        grammar_cache[language] = grammar

        logger.info(
            f"Successfully loaded and cached grammar for language: '{language}'"
        )
        return grammar

    except Exception as e:
        logger.error(f"Failed to load grammar for '{language}': {e}")
        raise ValueError(f"Could not load grammar for language '{language}'.")


class GeneralizerModel:
    _instance = None
    llm: Llama | None = None
    # We no longer need this, as it will be loaded dynamically
    # grammar: LlamaGrammar | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GeneralizerModel, cls).__new__(cls)
        return cls._instance

    def load(self):
        if not settings.model_path.exists():
            logger.critical(f"Model not found at {settings.model_path}.")
            raise FileNotFoundError(f"LLM model not found at {settings.model_path}.")

        # We no longer load the *global* grammar file
        # We also no longer need settings.grammar_path

        try:
            llm_params = settings.llm.params.model_dump()
            self.llm = Llama(
                model_path=str(settings.model_path),
                n_threads=int(os.cpu_count() or 4),
                **llm_params,
            )
            logger.success("✅ LLM Model loaded successfully.")

        except Exception as e:
            logger.critical(f"Failed to initialize the model: {e}")
            raise RuntimeError(f"Could not initialize the model: {e}")

    def predict(self, title: str, language: str) -> Dict[str, Any]:
        if not self.llm:
            raise RuntimeError("Model is not loaded. Call load() before predict().")

        try:
            # 1. Get the language-specific prompt function
            create_full_prompt = get_prompt_builder(language)
            # 2. Get the language-specific grammar object
            lang_grammar = get_language_grammar(language)
        except ValueError as e:
            raise e

        # 3. Create the full prompt
        full_prompt = create_full_prompt(title)

        prompt_tokens = self.llm.tokenize(full_prompt.encode("utf-8"))

        max_new_tokens = settings.llm.params.n_ctx - len(prompt_tokens) - 10
        max_new_tokens = min(max_new_tokens, settings.llm.params.max_tokens)

        if max_new_tokens <= 0:
            raise ValueError("Input prompt is too long for the context window.")

        # 4. Run inference using the language-specific grammar
        output = self.llm(
            prompt=full_prompt,
            grammar=lang_grammar,  # <-- Use the dynamic grammar
            max_tokens=max_new_tokens,
            stop=["<|im_end|>"],
        )

        raw_text = output["choices"][0]["text"].strip()

        # 5. Parse output
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            logger.error(f"JSON Decode Error. Raw output: '{raw_text}'")
            try:
                start = raw_text.find("{")
                end = raw_text.rfind("}")
                if start != -1 and end != -1:
                    clean_json = raw_text[start : end + 1]
                    return json.loads(clean_json)
            except json.JSONDecodeError:
                raise ValueError(f"Failed to parse JSON from model output: {raw_text}")
            raise ValueError(f"Failed to parse JSON from model output: {raw_text}")


generalizer_model = GeneralizerModel()
