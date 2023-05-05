from typing import Self, Any

from ptree.symbol.symbol import Symbol, Terminal, Nonterminal
from ptree.symbol.pool import SymbolPool


class ProductionRule:

    def __init__(self, left: Nonterminal, right: list[Symbol]):
        self.id = None
        self.left = left
        self.right = right
        self.handler = None

    @classmethod
    def from_string(cls, rule: str, symbol_pool: SymbolPool) -> Self:
        if '->' not in rule:
            raise ValueError(f'invalid rule: {rule}')
        left, right = rule.split('->')
        return cls(
            symbol_pool.get_nonterminal(left.strip()),
            [symbol_pool.get_symbol(right.strip()) for right in right.split()],
        )

    def __eq__(self, other: 'ProductionRule') -> bool:
        if isinstance(other, ProductionRule):
            return self.left == other.left and self.right == other.right
        return False

    def __hash__(self) -> int:
        return hash((self.left, tuple(self.right)))

    def __str__(self) -> str:
        return f'{self.left} -> {" ".join(map(str, self.right))}'

    def __repr__(self) -> str:
        return f'ProductionRule({str(self)})'


class ParseItem:

    def __init__(self, rule: ProductionRule, lookahead: Symbol, dot: int = 0):
        self.rule = rule
        self.lookahead = lookahead
        self.dot = dot

    def is_end(self) -> bool:
        return self.dot == len(self.rule.right) or self.rule.right[0].name == Grammar.NULL_SYMBOL_NAME

    def next(self) -> Symbol | None:
        if self.is_end():
            return None
        return self.rule.right[self.dot]

    @staticmethod
    def advance(item: 'ParseItem') -> 'ParseItem':
        item = ParseItem(item.rule, item.lookahead, item.dot)
        if item.is_end():
            raise RuntimeError(f'cannot advance a parse item at the end of a rule')
        item.dot += 1
        return item

    def __eq__(self, other: 'ParseItem') -> bool:
        if isinstance(other, ParseItem):
            return self.rule == other.rule and self.lookahead == other.lookahead and self.dot == other.dot
        return False

    def __hash__(self) -> int:
        return hash((self.rule, self.lookahead, self.dot))

    def __str__(self) -> str:
        return f'{self.rule.left.name} -> {" ".join([symbol.name for symbol in self.rule.right[:self.dot]])} ' \
               f'. {" ".join([symbol.name for symbol in self.rule.right[self.dot:]])}, {self.lookahead.name}'

    def __repr__(self) -> str:
        return f'ParseItem({str(self)})'


class ParseState:

    def __init__(self, symbol_pool: SymbolPool):
        self._symbol_pool = symbol_pool
        self.items = set()

    def _compute_head(self, symbols: list[Symbol]) -> set[Symbol]:
        head = set()
        for symbol in symbols:
            if isinstance(symbol, Nonterminal):
                head |= symbol.first
                if not symbol.nullable:
                    break
            else:
                head.add(symbol)
                if symbol.name != Grammar.NULL_SYMBOL_NAME:
                    break
        head.discard(self._symbol_pool.get_terminal(Grammar.NULL_SYMBOL_NAME))
        return head

    def closure(self):
        while True:
            new_items = set()
            for item in self.items:
                if item.is_end():
                    continue
                symbol = item.next()
                if isinstance(symbol, Nonterminal):
                    lookahead_symbols = item.rule.right[item.dot + 1:]
                    lookahead_symbols.append(item.lookahead)
                    head = self._compute_head(lookahead_symbols)
                    for rule in symbol.rules:
                        for lookahead in head:
                            new_items.add(ParseItem(rule, lookahead))
            if new_items.issubset(self.items):
                break
            self.items |= new_items

    def __eq__(self, other: 'ParseState') -> bool:
        if isinstance(other, ParseState):
            return self.items == other.items
        return False

    def __hash__(self) -> int:
        return hash(tuple(self.items))

    def __str__(self) -> str:
        return f'{{{"; ".join(map(str, self.items))}}}'

    def __repr__(self) -> str:
        return f'ParseState({str(self)})'


class Transition:
    TYPE_GOTO = 0
    TYPE_SHIFT = 1
    TYPE_REDUCE = 2
    TYPE_ACCEPT = 3

    def __init__(self, source: int, target: int | ProductionRule, symbol: Symbol, transition_type: int):
        self.source = source
        self.target = target
        self.symbol = symbol
        self.type = transition_type

    def __eq__(self, other: 'Transition') -> bool:
        if isinstance(other, Transition):
            return self.source == other.source and \
                   self.target == other.target and \
                   self.symbol == other.symbol and \
                   self.type == other.type
        return False

    def __hash__(self) -> int:
        return hash((self.source, self.target, self.symbol, self.type))

    def __str__(self) -> str:
        type_desc = {
            Transition.TYPE_GOTO: 'goto',
            Transition.TYPE_SHIFT: 'shift',
            Transition.TYPE_REDUCE: 'reduce',
            Transition.TYPE_ACCEPT: 'accept',
        }
        return f'{type_desc[self.type]}: {{{self.source}}} -> {{{self.target}}} on {self.symbol}'

    def __repr__(self) -> str:
        return f'Transition({str(self)})'


class ParseTable:

    def __init__(self,
                 config: dict[str, Any],
                 symbol_pool: SymbolPool,
                 start_symbol: Nonterminal):
        self.config = config
        self.symbol_pool = symbol_pool
        self.start_symbol = start_symbol
        self.transitions = {}

        state_list = []
        start_state = ParseState(self.symbol_pool)
        for rule in self.start_symbol.rules:
            item = ParseItem(rule=rule, lookahead=self.symbol_pool.get_terminal(Grammar.END_SYMBOL_NAME))
            start_state.items.add(item)
        start_state.closure()
        state_list.append(start_state)
        self.state_id_map = {start_state: 0}

        while True:
            state = state_list.pop(0)
            for item in state.items:
                if item.is_end():
                    transition_type = Transition.TYPE_REDUCE
                    if item.rule.left == self.start_symbol and \
                            item.lookahead == self.symbol_pool.get_terminal(Grammar.END_SYMBOL_NAME):
                        transition_type = Transition.TYPE_ACCEPT
                    self.transitions.setdefault(self.state_id_map[state], {})[item.lookahead] = Transition(
                        source=self.state_id_map[state],
                        target=item.rule,
                        symbol=item.lookahead,
                        transition_type=transition_type,
                    )
                else:
                    symbol = item.next()
                    new_state = ParseState(self.symbol_pool)
                    for item_ in state.items:
                        if item_.next() == symbol:
                            new_state.items.add(ParseItem.advance(item_))
                    new_state.closure()
                    if new_state not in self.state_id_map:
                        state_list.append(new_state)
                        self.state_id_map[new_state] = len(self.state_id_map)
                    if isinstance(symbol, Terminal):
                        transition_type = Transition.TYPE_SHIFT
                    else:
                        transition_type = Transition.TYPE_GOTO
                    self.transitions.setdefault(self.state_id_map[state], {})[symbol] = Transition(
                        source=self.state_id_map[state],
                        target=self.state_id_map[new_state],
                        symbol=symbol,
                        transition_type=transition_type,
                    )
            if not state_list:
                break


class Grammar:
    START_SYMBOL_NAME = '_S'
    NULL_SYMBOL_NAME = 'null'
    END_SYMBOL_NAME = '$'

    def __init__(self, config: dict[str, Any]):
        self._config = config
        self._start_symbol = None
        self._rules = None
        self.parse_table = None
        self.symbol_pool = SymbolPool(
            set(config['terminal_symbols'] or {}),
            set(config['nonterminal_symbols'] or []),
        )

    def init(self, rules: list[ProductionRule] | None = None):
        self._start_symbol = self.symbol_pool.get_nonterminal(self._config['start_symbol'])
        if rules is None:
            self._start_symbol, self._rules = self._augment()
        else:
            self._rules = rules
        for rule_id, rule in enumerate(self._rules):
            rule.id = rule_id
            rule.left.rules.append(rule)
        self._compute_nullable()
        self._compute_first()
        self.parse_table = ParseTable(
            config=self._config,
            symbol_pool=self.symbol_pool,
            start_symbol=self._start_symbol,
        )

    def _augment(self) -> tuple[Nonterminal, list[ProductionRule]]:
        augmented_start_symbol = self.symbol_pool.get_nonterminal(Grammar.START_SYMBOL_NAME)
        rules = [ProductionRule.from_string(rule, self.symbol_pool) for rule in self._config['production_rules']]
        rules.insert(0, ProductionRule(augmented_start_symbol, [self._start_symbol]))
        return augmented_start_symbol, rules

    def _compute_nullable(self):
        nullable = {self.symbol_pool.get_terminal(Grammar.NULL_SYMBOL_NAME)}
        while True:
            nullable_size = len(nullable)
            for rule in self._rules:
                if all(symbol in nullable for symbol in rule.right):
                    nullable.add(rule.left)
                    rule.left.nullable = True
            if len(nullable) == nullable_size:
                break

    def _compute_first(self):
        null_symbol = self.symbol_pool.get_terminal(Grammar.NULL_SYMBOL_NAME)
        while True:
            first_size = sum(len(symbol.first) for symbol in self.symbol_pool.get_symbols())
            for rule in self._rules:
                add_null = True
                for symbol in rule.right:
                    rule.left.first |= symbol.first - {null_symbol}
                    if null_symbol not in symbol.first:
                        add_null = False
                        break
                if add_null:
                    rule.left.first.add(null_symbol)
            if sum(len(symbol.first) for symbol in self.symbol_pool.get_symbols()) == first_size:
                break
