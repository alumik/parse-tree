from typing import *

from ptree.symbol.symbol import AbstractTerminal, AbstractNonterminal


class SymbolPool:

    def __init__(self, terminals: Set[str], nonterminals: Set[str]):
        from ptree.parser.grammar import Grammar
        keywords = {
            Grammar.NULL_SYMBOL_NAME: 'an empty string',
            Grammar.END_SYMBOL_NAME: 'the end of a production',
            Grammar.START_SYMBOL_NAME: 'the start symbol of the augmented grammar',
        }
        for name in keywords:
            if name in terminals or name in nonterminals:
                raise ValueError(f'{name} is a keyword for {keywords[name]} '
                                 f'and cannot be used as a terminal or nonterminal: ')
        self._terminals = {name: AbstractTerminal(name) for name in terminals}
        self._terminals[Grammar.NULL_SYMBOL_NAME] = AbstractTerminal(Grammar.NULL_SYMBOL_NAME)
        self._terminals[Grammar.END_SYMBOL_NAME] = AbstractTerminal(Grammar.END_SYMBOL_NAME)
        self._nonterminals = {name: AbstractNonterminal(name) for name in nonterminals}
        self._nonterminals[Grammar.START_SYMBOL_NAME] = AbstractNonterminal(Grammar.START_SYMBOL_NAME)

    def get_terminal(self, name: str) -> AbstractTerminal:
        if name not in self._terminals:
            raise ValueError(f'terminal symbol {name} is not defined')
        return self._terminals[name]

    def get_nonterminal(self, name: str) -> AbstractNonterminal:
        if name not in self._nonterminals:
            raise ValueError(f'nonterminal symbol {name} is not defined')
        return self._nonterminals[name]

    def get_symbol(self, name: str) -> Union[AbstractTerminal, AbstractNonterminal]:
        if name in self._terminals:
            return self._terminals[name]
        if name in self._nonterminals:
            return self._nonterminals[name]
        raise ValueError(f'symbol {name} is not defined')

    def get_terminals(self) -> Set[AbstractTerminal]:
        return set(self._terminals.values())

    def get_nonterminals(self) -> Set[AbstractNonterminal]:
        return set(self._nonterminals.values())

    def get_symbols(self) -> Set[Union[AbstractTerminal, AbstractNonterminal]]:
        return set(self._terminals.values()) | set(self._nonterminals.values())
