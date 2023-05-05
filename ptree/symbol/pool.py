from ptree.symbol.symbol import Terminal, Nonterminal


class SymbolPool:

    def __init__(self, terminals: set[str], nonterminals: set[str]):
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
        self._terminals = {name: Terminal(name) for name in terminals}
        self._terminals[Grammar.NULL_SYMBOL_NAME] = Terminal(Grammar.NULL_SYMBOL_NAME)
        self._terminals[Grammar.END_SYMBOL_NAME] = Terminal(Grammar.END_SYMBOL_NAME)
        self._nonterminals = {name: Nonterminal(name) for name in nonterminals}
        self._nonterminals[Grammar.START_SYMBOL_NAME] = Nonterminal(Grammar.START_SYMBOL_NAME)

    def get_terminal(self, name: str) -> Terminal:
        if name not in self._terminals:
            raise ValueError(f'terminal {name} is not defined')
        return self._terminals[name]

    def get_nonterminal(self, name: str) -> Nonterminal:
        if name not in self._nonterminals:
            raise ValueError(f'nonterminal {name} is not defined')
        return self._nonterminals[name]

    def get_symbol(self, name: str) -> Terminal | Nonterminal:
        if name in self._terminals:
            return self._terminals[name]
        if name in self._nonterminals:
            return self._nonterminals[name]
        raise ValueError(f'symbol {name} is not defined')

    def get_terminals(self) -> set[Terminal]:
        return set(self._terminals.values())

    def get_nonterminals(self) -> set[Nonterminal]:
        return set(self._nonterminals.values())

    def get_symbols(self) -> set[Terminal | Nonterminal]:
        return set(self._terminals.values()) | set(self._nonterminals.values())
