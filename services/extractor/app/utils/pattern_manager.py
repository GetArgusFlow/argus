import yaml
import re
from pathlib import Path
from typing import Dict, Pattern, List, Any
from loguru import logger

from app.config import settings
from app.core.context import shared_context

CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config/patterns.yml"
CUSTOM_CONFIG_PATH = CONFIG_PATH.parent / "custom_patterns.yml"


class PatternManager:
    def __init__(self, config_path: Path, custom_config_path: Path):
        self._all_patterns: Dict[str, Dict[str, Any]] = {}
        self._compiled_regex_cache: Dict[tuple, Pattern] = {}
        self._compiled_list_cache: Dict[tuple, List[str]] = {}

        self._load_and_merge(config_path, custom_config_path)

    def _deep_merge_dict(self, base: Dict, custom: Dict) -> Dict:
        """Merges custom config into base config."""
        for lang, patterns in custom.items():
            if lang not in base:
                base[lang] = patterns
                continue
            for key, value in patterns.items():
                if key not in base[lang]:
                    base[lang][key] = value
                # If both values are lists, combine them and remove duplicates
                elif isinstance(base[lang].get(key), list) and isinstance(value, list):
                    base[lang][key] = list(dict.fromkeys(base[lang][key] + value))
                # Otherwise, custom value overwrites base value (e.g., for regex)
                else:
                    base[lang][key] = value
        return base

    def _load_and_merge(self, base_path: Path, custom_path: Path):
        """Loads and merges base and custom pattern files."""
        logger.info(f"PatternManager: Loading base patterns from {base_path}...")
        base_patterns = {}
        try:
            with open(base_path, "r", encoding="utf-8") as f:
                base_patterns = yaml.safe_load(f) or {}
            logger.success("PatternManager: Base patterns loaded.")
        except FileNotFoundError:
            logger.error(
                f"PatternManager FATAL: Base config file not found at {base_path}"
            )
            # We can continue with an empty base, but it's not ideal
        except Exception as e:
            logger.error(f"Error loading base patterns: {e}")

        custom_patterns = {}
        if custom_path.exists():
            logger.info(
                f"PatternManager: Loading custom patterns from {custom_path}..."
            )
            try:
                with open(custom_path, "r", encoding="utf-8") as f:
                    custom_patterns = yaml.safe_load(f) or {}
                logger.success("PatternManager: Custom patterns loaded.")
            except Exception as e:
                logger.error(f"Error loading custom patterns: {e}")
        else:
            logger.debug(
                "PatternManager: No custom_patterns.yml found. Using base patterns only."
            )

        # Perform the deep merge
        self._all_patterns = self._deep_merge_dict(base_patterns, custom_patterns)
        logger.info(
            f"PatternManager initialized with {len(self._all_patterns)} language(s)."
        )

    def _get_active_languages(self) -> List[str]:
        """
        Gets the detected lang for the current request and the default fallback lang.
        Returns an ordered, unique list, e.g., ['nl', 'en'] or just ['en'].
        """
        lang_code = shared_context.get("lang_code", default=settings.language.default)

        # Use dict.fromkeys to get a unique, ordered list
        langs_to_check = [lang_code]
        if settings.language.default not in langs_to_check:
            langs_to_check.append(settings.language.default)

        return langs_to_check

    def get_keyword_list(self, pattern_name: str) -> List[str]:
        """
        Gets a combined list of keywords for all active languages (request-specific).
        e.g., for 'availability_in_stock', returns Dutch AND English keywords.
        """
        langs = self._get_active_languages()
        cache_key = (tuple(sorted(langs)), pattern_name)

        if cache_key in self._compiled_list_cache:
            return self._compiled_list_cache[cache_key]

        combined_list = []
        for lang in langs:
            lang_patterns = self._all_patterns.get(lang, {})
            keywords = lang_patterns.get(pattern_name, [])
            if isinstance(keywords, list):
                combined_list.extend(keywords)
            elif keywords:
                logger.warning(
                    f"PatternManager: Pattern '{pattern_name}' for lang '{lang}' is not a list."
                )

        # De-duplicate the list
        final_list = list(dict.fromkeys(combined_list))
        self._compiled_list_cache[cache_key] = final_list
        return final_list

    def get_compiled_regex(self, pattern_name: str) -> Pattern:
        """
        Gets a combined, compiled regex pattern for all active languages (request-specific).
        e.g., for 'brand_class_regex', returns (nl_pattern|en_pattern)
        """
        langs = self._get_active_languages()
        # Use a tuple of sorted langs as the cache key
        cache_key = (tuple(sorted(langs)), pattern_name)

        if cache_key in self._compiled_regex_cache:
            return self._compiled_regex_cache[cache_key]

        combined_pattern_parts = []
        for lang in langs:
            lang_patterns = self._all_patterns.get(lang, {})
            pattern_str = lang_patterns.get(pattern_name)
            if pattern_str and isinstance(pattern_str, str):
                combined_pattern_parts.append(
                    f"({pattern_str})"
                )  # Group each lang's pattern
            elif pattern_str:
                logger.warning(
                    f"PatternManager: Pattern '{pattern_name}' for lang '{lang}' is not a string."
                )

        if not combined_pattern_parts:
            logger.warning(
                f"No regex pattern found for '{pattern_name}' in active langs {langs}. This regex will not match anything."
            )
            # Return a regex that never matches
            return re.compile(r"a^")

        # Join all patterns with an OR operator
        final_pattern_str = "|".join(combined_pattern_parts)
        compiled_regex = re.compile(final_pattern_str, re.IGNORECASE)

        self._compiled_regex_cache[cache_key] = compiled_regex
        return compiled_regex


# Create a single global instance that can be imported anywhere in the app.
pattern_manager = PatternManager(
    config_path=CONFIG_PATH, custom_config_path=CUSTOM_CONFIG_PATH
)
