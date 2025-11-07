# argus/services/llm_parser/app/config.py

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, Field
from pathlib import Path
from typing import Any, Tuple, Dict

# Define the project's root directory
BASE_DIR = Path(__file__).resolve().parent.parent


def yaml_config_settings_source() -> Dict[str, Any]:
    """
    A custom settings source that loads variables from a YAML file.
    """
    yaml_config_path = BASE_DIR / "config/config.yml"
    try:
        with open(yaml_config_path, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(
            f"WARNING: YAML config file not found at {yaml_config_path}, using defaults and .env only."
        )
        return {}


# Pydantic models for nested structures
class ServiceSettings(BaseModel):
    host: str
    port: int
    log_level: str
    log_dir: str
    environment: str


class LLMSourceSettings(BaseModel):
    directory: str
    filename: str
    url: str


class LLMParamsSettings(BaseModel):
    n_ctx: int = Field(alias="n_ctx")
    n_gpu_layers: int = Field(alias="n_gpu_layers")
    max_tokens: int
    temperature: float


class LLMSettings(BaseModel):
    source: LLMSourceSettings
    params: LLMParamsSettings


class ToolsSettings(BaseModel):
    grammar_script_url: str


class AuthSettings(BaseModel):
    api_key: str


# The main Settings class
class Settings(BaseSettings):
    """Main configuration model for the LLM Parser service."""

    service: ServiceSettings
    llm: LLMSettings
    tools: ToolsSettings
    auth: AuthSettings
    data_dir: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_file_encoding="utf-8", env_nested_delimiter="__"
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ) -> Tuple[Any, ...]:
        # Define the priority of settings sources
        return (
            env_settings,
            dotenv_settings,
            yaml_config_settings_source,
            init_settings,
            file_secret_settings,
        )

    # These properties remain very useful for deriving paths
    @property
    def model_path(self) -> Path:
        return BASE_DIR / self.llm.source.directory / self.llm.source.filename

    @property
    def grammar_path(self) -> Path:
        return BASE_DIR / self.data_dir / "grammar.gbnf"


# Create a single, global 'settings' instance for the application to use.
settings = Settings()
