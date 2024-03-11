from functools import lru_cache
from typing import Dict, List

from .base import BaseAPI
from ..config import get_config


class APIRegistry:
    def __init__(self):
        self.apis: List[BaseAPI] = []

    def register(self, api: BaseAPI):
        self.apis.append(api)


@lru_cache
def get_registry() -> APIRegistry:
    config = get_config()
    registry = APIRegistry()

    from .core import CoreAPI
    from .maps import MapsAPI

    api_config: Dict[str, bool] = config.get("apis")
    include_maps = api_config.get("maps")
    include_coverages = api_config.get("coverages")

    if include_maps or include_coverages:
        registry.register(CoreAPI())

    if include_maps:
        registry.register(MapsAPI())

    if include_coverages:
        pass

    return registry
