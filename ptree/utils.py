import yaml

from typing import *


def load_config(path: str) -> Dict[str, Any]:
    with open(path, 'r') as f:
        config = yaml.safe_load(f)
    return config
