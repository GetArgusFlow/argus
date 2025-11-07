# app/core/prompt.py

import json
from loguru import logger

# Try to import examples; if they don't exist, continue without them.
try:
    from data.examples import json_examples
except ImportError:
    logger.warning("data/examples.py not found, skipping few-shot examples.")
    json_examples = []


def build_prompt_template() -> str:
    """Create the complete prompt template including few-shot examples."""

    system_prompt = (
        "[INST]\n"
        "You are an expert HTML parser. Your task is to convert the provided HTML fragment into a logically structured JSON object.\n"
        "- The 'category' field should be derived from the HTML. It is most commonly an title just before the specifications list. \n"
        "- The 'details' field can be a key-value object or a list of strings.\n"
        "The output must ONLY be the JSON code, perfectly following the provided schema.\n"
        "[/INST]\n\n"
    )

    few_shot_section = ""
    for example in json_examples:
        if "html" in example and "json" in example:
            # Convert the example JSON to a compact string
            json_output_string = json.dumps(example["json"])

            escaped_json_string = json_output_string.replace("{", "{{").replace(
                "}", "}}"
            )

            few_shot_section += f"[HTML]\n{example['html']}\n[/HTML]\n\n[JSON]\n{escaped_json_string}\n\n"

    return (
        system_prompt + few_shot_section + "[HTML]\n{html_snippet}\n[/HTML]\n\n[JSON]\n"
    )


# Initialize the prompt template when the module is loaded
PROMPT_TEMPLATE = build_prompt_template()
