import os
from functools import lru_cache

import yaml

CONFIG_PATH = os.environ.get("STACTURE_CONFIG_PATH", "/etc/stacture/config.yaml")


@lru_cache
def get_config() -> dict:
    print("loading config")
    with open(CONFIG_PATH) as f:
        return yaml.load(f)
