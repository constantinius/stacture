from typing import Set
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    title: str = "stacture API"
    description: str = ""
    attribution: str = ""
    apis: Set[str] = {"maps", "coverages"}

    model_config = SettingsConfigDict(env_prefix='stacture_')


@lru_cache
def get_settings() -> Settings:
    return Settings()
