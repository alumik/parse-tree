import yaml

from typing import *


def load_config(path: str) -> Dict[str, Any]:
    with open(path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def escaper(s: str) -> str:
    return s \
        .replace('\\', '\\\\') \
        .replace('\r', '\\\\r') \
        .replace('\n', '\\\\n') \
        .replace('\t', '\\\\t') \
        .replace('\f', '\\\\f')
