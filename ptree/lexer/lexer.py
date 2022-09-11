from typing import *

from ptree.lexer.fsm import NFA
from ptree.lexer.regex import Regex, RegexEngine
from ptree.symbol.symbol import Symbol
from ptree.parser.grammar import SymbolPool


class Lexer:

    def __init__(self, config: Dict[str, Any], symbol_pool: SymbolPool):
        self._config = config
        self._symbol_pool = symbol_pool
        self._symbol_names_and_patterns = self._config['terminal_symbols']
        self._ignored_symbols = self._config['ignored_symbols']
        regex_engine = RegexEngine()
        nfa_list = [
            regex_engine.parse(Regex(name, pattern)) for name, pattern in self._symbol_names_and_patterns.items()
        ]
        self._dfa = NFA.union(nfa_list).to_dfa()
        self._dfa.start.dfs(
            action=lambda state: state.accept_list.sort(
                key=lambda x: list(self._symbol_names_and_patterns).index(x),
            ),
        )

    def tokenize(self, text: str) -> List[Symbol]:
        result = []
        while text:
            match self._dfa.match(text):
                case None:
                    raise ValueError(f'unexpected character: {text[0]}')
                case (symbol_name, matched_idx):
                    if symbol_name not in self._ignored_symbols:
                        result.append(Symbol(text[:matched_idx], self._symbol_pool.get_terminal(symbol_name)))
                    text = text[matched_idx:]
        return result
