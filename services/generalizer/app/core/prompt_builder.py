# argus/services/generalizer/app/core/prompt_builder.py

import json
from typing import List, Dict, Any
# We no longer import settings here


class PromptBuilder:
    """
    Builds the complete model prompt from language-specific data.
    """

    def __init__(
        self,
        system_prompt_template: str,
        examples: List[Dict[str, Any]],
        user_prefix: str,
        categories_list: List[str],
    ):
        self.json_suffix = "\n<|im_start|>assistant\n"
        self.user_prefix = user_prefix.strip() + " "

        # 1. Inject categories into the system prompt template
        categories_json = json.dumps(categories_list)
        self.system_prompt = system_prompt_template.format(
            CATEGORIES_JSON=categories_json
        )

        # 2. Build the few-shot section
        self.few_shot_section = self._build_few_shot_prompt(examples)

        # 3. Create the final static prefix
        self.static_prompt_prefix = f"{self.system_prompt}{self.few_shot_section}<|im_start|>user\n{self.user_prefix}"

    def _build_few_shot_prompt(self, examples: List[Dict[str, Any]]) -> str:
        """
        Builds the few-shot example string from the list of examples.
        """
        few_shot_section = ""
        for example in examples:
            few_shot_section += f"<|im_start|>user\n{self.user_prefix}{example['title']}\n<|im_start|>assistant\n{json.dumps(example['json'])}<|im_end|>\n"
        return few_shot_section

    def create_full_prompt(self, title: str) -> str:
        """
        Creates the full, final prompt for the model.
        """
        return f"{self.static_prompt_prefix}{title}{self.json_suffix}"
