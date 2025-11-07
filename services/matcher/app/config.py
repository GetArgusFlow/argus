# argus/services/matcher/app/config.py

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Any, Dict, Tuple

# Define the project's root directory
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


# Pydantic models for nested structures
class ServiceSettings(BaseModel):
    host: str
    port: int
    log_level: str
    environment: str


class DatabaseSettings(BaseModel):
    host: str
    user: str
    password: str
    name: str
    port: int


class MatcherSettings(BaseModel):
    base_model_name: str
    device: str
    models_dir: str
    finetuned_model_dir: str
    faiss_index_path: str
    id_map_path: str
    batch_size: int
    epochs: int
    top_k_default: int
    autosave_every: int


class AuthSettings(BaseModel):
    api_key: str = Field("default_dev_key", min_length=15)


# Pydantic model for the database queries
class DatabaseQuerySettings(BaseModel):
    training_pairs_query: str
    indexing_query: str
    product_by_id_query: str = Field(..., pattern=r".*:ids.*")  # Enforce placeholder


# The main Settings class
class Settings(BaseSettings):
    """Main configuration model for the Matcher service."""

    service: ServiceSettings
    database: DatabaseSettings
    matcher: MatcherSettings
    database_queries: DatabaseQuerySettings
    auth: AuthSettings

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
        return (
            env_settings,
            dotenv_settings,
            yaml_config_settings_source,
            init_settings,
        )

    # Derived properties for convenience
    @property
    def mysql_uri(self) -> str:
        db = self.database
        return f"mysql+pymysql://{db.user}:{db.password}@{db.host}:{db.port}/{db.name}"

    @property
    def finetuned_model_path(self) -> Path:
        return BASE_DIR / self.matcher.finetuned_model_dir

    @property
    def index_path(self) -> Path:
        return BASE_DIR / self.matcher.faiss_index_path

    @property
    def id_map_path(self) -> Path:
        return BASE_DIR / self.matcher.id_map_path


# Global settings instance
settings = Settings()
