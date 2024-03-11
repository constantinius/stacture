from functools import lru_cache

from .base import BaseSource
from .stac_api import STACAPISource
from ..config import get_config


@lru_cache
def get_source(source_id: str) -> BaseSource:
    config = get_config()

    source_cfg = config["sources"][source_id]
    source_type = source_cfg.pop("type")
    if source_type == "stac-api":
        return STACAPISource(**source_cfg)
    else:
        ...
