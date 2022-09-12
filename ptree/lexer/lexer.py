from typing import *

from ptree.symbol.symbol import Token
from ptree.symbol.pool import SymbolPool
from ptree.lexer.fsm import NFA
from ptree.lexer.regex import Regex, RegexEngine


class Lexer:

    def __init__(self, config: Dict[str, Any], symbol_pool: SymbolPool):
        self._config = config
        self._symbol_pool = symbol_pool
        self._symbol_names_and_patterns = self._config['terminal_symbols'] or {}
        self._ignored_symbols = self._config['ignored_symbols'] or []
        engine = RegexEngine()
        nfa_list = [
            engine.parse(Regex(name, pattern)) for name, pattern in self._symbol_names_and_patterns.items()
        ]
        self._dfa = NFA.union(nfa_list).to_dfa()
        self._dfa.start.dfs(
            action=lambda state: state.accept_list.sort(
                key=lambda x: list(self._symbol_names_and_patterns).index(x),
            ),
        )

    def tokenize(self, text: str) -> List[Token]:
        result = []
        while text:
            match self._dfa.match(text):
                case None:
                    raise ValueError(f'unexpected character: {text[0]}')
                case (symbol_name, matched_idx):
                    if symbol_name not in self._ignored_symbols:
                        result.append(
                            Token(value=text[:matched_idx], symbol=self._symbol_pool.get_terminal(symbol_name))
                        )
                    text = text[matched_idx:]
        return result
