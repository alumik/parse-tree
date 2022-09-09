class AbstractSymbol:
    TYPE_TERMINAL = 0
    TYPE_NONTERMINAL = 1

    def __init__(self, name: str):
        self.name = name
        self.first = set()

    @property
    def type(self) -> int:
        raise NotImplementedError()

    def __eq__(self, other: 'AbstractSymbol') -> bool:
        if isinstance(other, AbstractSymbol):
            return self.name == other.name and self.type == other.type
        return False

    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'AbstractSymbol({self.name})'


class AbstractTerminal(AbstractSymbol):

    def __init__(self, name: str):
        super().__init__(name)
        self.first.add(self)

    @property
    def type(self) -> int:
        return AbstractSymbol.TYPE_TERMINAL

    def __repr__(self) -> str:
        return f'AbstractTerminal({self.name})'


class AbstractNonterminal(AbstractSymbol):

    def __init__(self, name: str):
        super().__init__(name)
        self.nullable = False
        self.rules = []

    @property
    def type(self) -> int:
        return AbstractSymbol.TYPE_NONTERMINAL

    def __repr__(self) -> str:
        return f'AbstractNonterminal({self.name}, nullable={self.nullable})'


class Symbol:

    def __init__(self, value: str, abstract: AbstractSymbol):
        self.value = value
        self.abstract = abstract

    def __eq__(self, other: 'Symbol') -> bool:
        if isinstance(other, Symbol):
            return self.value == other.value and self.abstract == other.abstract
        return False

    def __hash__(self) -> int:
        return hash((self.value, self.abstract))

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f'Symbol({self.value}, abstract={repr(self.abstract)})'
