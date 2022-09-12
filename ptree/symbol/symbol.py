class Symbol:
    TYPE_TERMINAL = 0
    TYPE_NONTERMINAL = 1

    def __init__(self, name: str):
        self.name = name
        self.first = set()

    @property
    def type(self) -> int:
        raise NotImplementedError()

    def __eq__(self, other: 'Symbol') -> bool:
        if isinstance(other, Symbol):
            return self.name == other.name and self.type == other.type
        return False

    def __hash__(self) -> int:
        return hash((self.name, self.type))

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'Symbol({str(self)})'


class Terminal(Symbol):

    def __init__(self, name: str):
        super().__init__(name)
        self.first.add(self)

    @property
    def type(self) -> int:
        return Symbol.TYPE_TERMINAL

    def __repr__(self) -> str:
        return f'Terminal({str(self)})'


class Nonterminal(Symbol):

    def __init__(self, name: str):
        super().__init__(name)
        self.nullable = False
        self.rules = []

    @property
    def type(self) -> int:
        return Symbol.TYPE_NONTERMINAL

    def __repr__(self) -> str:
        return f'Nonterminal({str(self)}, nullable={self.nullable})'


class Token:

    def __init__(self, value: str, symbol: Symbol):
        self.value = value
        self.symbol = symbol

    def __eq__(self, other: 'Token') -> bool:
        if isinstance(other, Token):
            return self.value == other.value and self.symbol == other.symbol
        return False

    def __hash__(self) -> int:
        return hash((self.value, self.symbol))

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f'Token({str(self)}, symbol={repr(self.symbol)})'
