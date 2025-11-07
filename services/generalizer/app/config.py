# argus/services/generalizer/app/config.py

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Any, Dict, Tuple

# Define the service's root directory
BASE_DIR = Path(__file__).resolve().parent.parent


def yaml_config_settings_source() -> Dict[str, Any]:
    """
    A custom settings source that loads variables from a YAML file.
    """
    yaml_config_path = BASE_DIR / "config/config.yml"
    try:
        with open(yaml_config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"WARNING: YAML config file not found at {yaml_config_path}.")
        return {}


# Pydantic models for the nested YAML structure


class ServiceSettings(BaseModel):
    host: str
    port: int
    log_level: str
    environment: str
    default_language: str


class LLMSourceSettings(BaseModel):
    directory: str
    filename: str
    url: str


class LLMParamsSettings(BaseModel):
    n_ctx: int
    n_gpu_layers: int
    max_tokens: int
    temperature: float
    n_batch: int
    verbose: bool


class LLMSettings(BaseModel):
    source: LLMSourceSettings
    params: LLMParamsSettings


class ToolsSettings(BaseModel):
    grammar_script_url: str


class AuthSettings(BaseModel):
    api_key: str


# The main Settings class


class Settings(BaseSettings):
    """Main configuration for the Generalizer Service."""

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
        # Priority of sources: .env > config.yml > defaults
        return (
            env_settings,
            dotenv_settings,
            yaml_config_settings_source,
            init_settings,
            file_secret_settings,
        )

    # Properties to dynamically generate the correct paths
    @property
    def model_path(self) -> Path:
        # Paths in YAML are relative; here we make them absolute.
        return (
            BASE_DIR / self.llm.source.directory / self.llm.source.filename
        ).resolve()

    @property
    def grammar_path(self) -> Path:
        return (BASE_DIR / self.data_dir / "grammar.gbnf").resolve()


# Global, single instance of the settings for the entire application
settings = Settings()
