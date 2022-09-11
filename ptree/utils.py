import yaml

from typing import *

from ptree.symbol.symbol import Symbol


def load_config(path: str) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def escaper(s: str) -> str:
    return s \
        .replace('\\', '\\\\') \
        .replace('\r', '\\\\r') \
        .replace('\n', '\\\\n') \
        .replace('\t', '\\\\t') \
        .replace('\f', '\\\\f')


def pretty_print_tokens(tokens: List[Symbol]):
    from dashtable import data2rst
    table = [['', 'SYMBOL', 'VALUE']]
    for i, token in enumerate(tokens):
        table.append([str(i + 1), token.abstract.name, token.value])
    print(data2rst(table))
