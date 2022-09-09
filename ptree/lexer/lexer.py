from typing import *

from ptree import Parser
from ptree.lexer.regex import Regex, RegexEngine
from ptree.lexer.fsm import NFA


class Lexer:

    def __init__(self, config: Dict[str, Any], parser: Parser):
        self._config = config
        self._parser = parser
        self._accept_rules = self._config['terminal_symbols']
        self._ignored_symbols = self._config['ignored_symbols']
        regex_engine = RegexEngine()
        nfa_list = []
        for name, regex in self._accept_rules:
            nfa_list.append(regex_engine.parse(Regex(name, regex)))
        self._dfa = NFA.union(nfa_list).to_dfa()
