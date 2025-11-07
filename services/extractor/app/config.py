# argus/services/extractor/app/config.py

import yaml
import re
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, Field, field_validator
from pathlib import Path
from typing import List, Any, Tuple, Dict

# Define the project's root directory
BASE_DIR = Path(__file__).resolve().parent.parent


class PatternDetail(BaseModel):
    description: str
    examples: list[str]
    pattern: str

    @field_validator("pattern")
    def valid_regex(cls, v):
        try:
            re.compile(v)
        except re.error as e:
            raise ValueError(f"'{v}' is not a valid regular expression: {e}")
        return v


def yaml_config_settings_source() -> Dict[str, Any]:
    """
    A custom settings source that loads variables from a YAML file.
    It must accept 'settings_cls' as an argument to be compatible.
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
    llm_parser_url: str
    host: str
    port: int
    log_level: str
    log_dir: str
    environment: str


class HtmlPreprocessingSettings(BaseModel):
    noise_selectors: List[str]


class ModelsSettings(BaseModel):
    nlp: str


class LanguageSettings(BaseModel):
    default: str


class AuthSettings(BaseModel):
    api_key: str


# The main Settings class
class Settings(BaseSettings):
    """The main settings model using a custom YAML source."""

    service: ServiceSettings
    auth: AuthSettings
    html_preprocessing: HtmlPreprocessingSettings
    models: ModelsSettings
    field_aliases: Dict[str, List[str]] = Field(default_factory=dict)
    language: LanguageSettings

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
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


# Create a single, global 'settings' instance for the application to use.
settings = Settings()
