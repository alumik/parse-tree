from typing import *

from ptree.parser.grammar import Grammar


class Parser:

    def __init__(self, config: Dict[str, Any]):
        self._grammar = Grammar(config)

    def parse(self, tokens: List[str]):
        pass
