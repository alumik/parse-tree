from typing import *
from copy import copy

from ptree.symbol.symbol import AbstractSymbol, AbstractNonterminal
from ptree.symbol.pool import SymbolPool


class ProductionRule:

    def __init__(self, left: AbstractNonterminal, right: List[AbstractSymbol]):
        self.id = None
        self.left = left
        self.right = right

    @classmethod
    def from_string(cls, rule_str: str, symbol_pool: SymbolPool) -> 'ProductionRule':
        if '->' not in rule_str:
            raise ValueError(f'invalid rule: {rule_str}')
        left, right = rule_str.split('->')
        return cls(
            symbol_pool.get_nonterminal(left.strip()),
            [symbol_pool.get_symbol(right.strip()) for right in right.split()],
        )

    def __copy__(self) -> 'ProductionRule':
        return ProductionRule(self.left, [symbol for symbol in self.right])

    def __eq__(self, other: 'ProductionRule') -> bool:
        if isinstance(other, ProductionRule):
            return self.left == other.left and self.right == other.right
        return False

    def __hash__(self) -> int:
        return hash((self.left, tuple(self.right)))

    def __str__(self) -> str:
        return f'{self.left} -> {" ".join(map(str, self.right))}'

    def __repr__(self) -> str:
        return f'ProductionRule({self.__str__()})'


class ParseItem:

    def __init__(self, rule: ProductionRule, lookahead: AbstractSymbol, dot: int = 0):
        self.rule = rule
        self.lookahead = lookahead
        self.dot = dot

    def is_end(self) -> bool:
        return self.dot == len(self.rule.right) or self.rule.right[0].name == Grammar.NULL_SYMBOL_NAME

    def next(self) -> Optional[AbstractSymbol]:
        if self.is_end():
            return None
        return self.rule.right[self.dot]

    def advance(self) -> 'ParseItem':
        if self.is_end():
            raise RuntimeError(f'cannot advance a parse item at the end of a rule')
        self.dot += 1
        return self

    def __copy__(self) -> 'ParseItem':
        return ParseItem(self.rule, self.lookahead, self.dot)

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
        return f'ParseItem({self.__str__()})'


class ParseState:

    def __init__(self, symbol_pool: SymbolPool):
        self._symbol_pool = symbol_pool
        self.items = set()

    def _compute_head(self, symbols: List[AbstractSymbol]) -> Set[AbstractSymbol]:
        head = set()
        for symbol in symbols:
            if isinstance(symbol, AbstractNonterminal):
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
                if symbol.type == AbstractSymbol.TYPE_NONTERMINAL:
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
        return f'ParseState({self.__str__()})'


class Transition:
    TYPE_GOTO = 0
    TYPE_SHIFT = 1
    TYPE_REDUCE = 2

    def __init__(self, source: int, target: Union[int, ProductionRule], on: AbstractSymbol, transition_type: int):
        self.source = source
        self.target = target
        self.on = on
        self.type = transition_type

    def __eq__(self, other: 'Transition') -> bool:
        if isinstance(other, Transition):
            return self.source == other.source and \
                   self.target == other.target and \
                   self.on == other.on and \
                   self.type == other.type
        return False

    def __hash__(self) -> int:
        return hash((self.source, self.target, self.on, self.type))

    def __str__(self) -> str:
        type_desc = {
            Transition.TYPE_GOTO: 'goto',
            Transition.TYPE_SHIFT: 'shift',
            Transition.TYPE_REDUCE: 'reduce',
        }
        return f'{type_desc[self.type]}: {{{self.source}}} -> {{{self.target}}} on {self.on}'

    def __repr__(self) -> str:
        return f'Transition({self.__str__()})'


class ParseTable:

    def __init__(self,
                 config: Dict[str, Any],
                 symbol_pool: SymbolPool,
                 start_symbol: AbstractNonterminal):
        self._config = config
        self._symbol_pool = symbol_pool
        self._start_symbol = start_symbol
        self.transitions = {}
        self.accept_state = None

        state_list = []
        start_state = ParseState(self._symbol_pool)
        for rule in self._start_symbol.rules:
            item = ParseItem(rule, self._symbol_pool.get_terminal(Grammar.END_SYMBOL_NAME))
            start_state.items.add(item)
        start_state.closure()
        state_list.append(start_state)
        self.states = {start_state: 0}

        while True:
            state = state_list.pop(0)
            for item in state.items:
                if item.is_end():
                    self.transitions.setdefault(self.states[state], {})[item.lookahead] = Transition(
                        self.states[state],
                        item.rule,
                        item.lookahead,
                        Transition.TYPE_REDUCE,
                    )
                    if item.rule.left == self._start_symbol and item.lookahead == self._symbol_pool.get_terminal(
                            Grammar.END_SYMBOL_NAME):
                        self.accept_state = state
                else:
                    symbol = item.next()
                    new_state = ParseState(self._symbol_pool)
                    for item_ in state.items:
                        if item_.next() == symbol:
                            new_state.items.add(copy(item_).advance())
                    new_state.closure()
                    if new_state not in self.states:
                        state_list.append(new_state)
                        self.states[new_state] = len(self.states)
                    if symbol.type == AbstractSymbol.TYPE_TERMINAL:
                        transition_type = Transition.TYPE_SHIFT
                    else:
                        transition_type = Transition.TYPE_GOTO
                    self.transitions.setdefault(self.states[state], {})[symbol] = Transition(
                        self.states[state],
                        self.states[new_state],
                        symbol,
                        transition_type,
                    )
            if not state_list:
                break

    def __str__(self) -> str:
        from dashtable import data2rst
        terminals = list(self._config['terminal_symbols'].keys())
        nonterminals = list(self._config['nonterminal_symbols'].keys())
        terminals.append(Grammar.END_SYMBOL_NAME)
        table = [
            [
                '',
                'ACTION',
                *['' for _ in range(len(terminals) - 1)],
                'GOTO',
                *['' for _ in range(len(nonterminals) - 1)],
                'STATE',
            ],
            ['', *terminals, *nonterminals, ''],
        ]
        for state, state_id in self.states.items():
            row = [state_id]
            for name in terminals + nonterminals:
                symbol = self._symbol_pool.get_symbol(name)
                if symbol in self.transitions[state_id]:
                    transition = self.transitions[state_id][symbol]
                    if transition.type == Transition.TYPE_SHIFT:
                        row.append(f's{transition.target}')
                    elif transition.type == Transition.TYPE_REDUCE:
                        row.append(f'r{transition.target.id}')
                    else:
                        row.append(f'{transition.target}')
                else:
                    row.append('')
            row.append(str(state))
            table.append(row)
        action_span = [[0, i + 1] for i in range(len(terminals))]
        goto_span = [[0, i + 1] for i in range(len(terminals), len(terminals) + len(nonterminals))]
        return data2rst(table, spans=[action_span, goto_span])


class Grammar:
    START_SYMBOL_NAME = '_S'
    NULL_SYMBOL_NAME = 'null'
    END_SYMBOL_NAME = '$'

    def __init__(self, config: Dict[str, Any]):
        self._config = config
        self.symbol_pool = SymbolPool(set(config['terminal_symbols']), set(config['nonterminal_symbols']))
        self.start_symbol = None
        self.rules = None
        self.parse_table = None

    def init(self, rules: Optional[List[ProductionRule]] = None):
        self.start_symbol = self.symbol_pool.get_nonterminal(self._config['start_symbol'])
        if rules is None:
            self.start_symbol, self.rules = self._augment()
        else:
            self.rules = rules
        for rule_id, rule in enumerate(self.rules):
            rule.id = rule_id
            rule.left.rules.append(rule)
        self._compute_nullable()
        self._compute_first()
        self.parse_table = ParseTable(
            config=self._config,
            symbol_pool=self.symbol_pool,
            start_symbol=self.start_symbol,
        )

    def _augment(self) -> Tuple[AbstractNonterminal, List[ProductionRule]]:
        augmented_start_symbol = self.symbol_pool.get_nonterminal(Grammar.START_SYMBOL_NAME)
        rules = [ProductionRule.from_string(rule, self.symbol_pool) for rule in self._config['production_rules']]
        rules.insert(0, ProductionRule(augmented_start_symbol, [self.start_symbol]))
        return augmented_start_symbol, rules

    def _compute_nullable(self):
        nullable = {self.symbol_pool.get_terminal(Grammar.NULL_SYMBOL_NAME)}
        while True:
            nullable_size = len(nullable)
            for rule in self.rules:
                if all(symbol in nullable for symbol in rule.right):
                    nullable.add(rule.left)
                    rule.left.nullable = True
            if len(nullable) == nullable_size:
                break

    def _compute_first(self):
        null_symbol = self.symbol_pool.get_terminal(Grammar.NULL_SYMBOL_NAME)
        while True:
            first_size = sum(len(symbol.first) for symbol in self.symbol_pool.get_symbols())
            for rule in self.rules:
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
