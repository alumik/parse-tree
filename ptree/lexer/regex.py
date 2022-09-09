from typing import *

from ptree.symbol.symbol import AbstractSymbol, AbstractNonterminal, Symbol
from ptree.symbol.pool import SymbolPool
from ptree.lexer.fsm import NFA
from ptree.parser.grammar import Grammar, ProductionRule


class Regex:

    def __init__(self, name: str, regex: str):
        self._name = name
        self._regex = regex

    def get_symbols(self, symbol_pool: SymbolPool) -> List[Symbol]:
        symbols = []
        char_symbol = symbol_pool.get_terminal('char')
        i = 0
        while i < len(self._regex):
            match c := self._regex[i]:
                case '\\':
                    i += 1
                    if i >= len(self._regex):
                        raise ValueError(f'invalid regex: {self._regex}')
                    match c_ := self._regex[i]:
                        case '-' | '+' | '*' | '|' | '[' | ']' | '(' | '^' | '.' | ')':
                            symbols.append(Symbol(c_, char_symbol))
                        case 'r':
                            symbols.append(Symbol('\r', char_symbol))
                        case 'n':
                            symbols.append(Symbol('\n', char_symbol))
                        case 't':
                            symbols.append(Symbol('\t', char_symbol))
                        case 'f':
                            symbols.append(Symbol('\f', char_symbol))
                        case '\\':
                            symbols.append(Symbol('\\', char_symbol))
                case '-' | '+' | '*' | '|' | '[' | ']' | '(' | '^' | '.' | ')':
                    symbols.append(Symbol(c, symbol_pool.get_terminal(c)))
                case _:
                    symbols.append(Symbol(c, char_symbol))
            i += 1
        return symbols

    def __str__(self):
        return f'{self._name} -> {self._regex}'

    def __repr__(self):
        return f'Regex({self.__str__()})'


class RegexProductionRule(ProductionRule):

    def __init__(self, left: AbstractNonterminal, right: List[AbstractSymbol]):
        super().__init__(left, right)
        self.handler = None


class RegexEngine:
    TERMINALS = {'|', '(', ')', '*', '+', '[', ']', '-', 'char', '^', '.'}
    NONTERMINALS = {'E', 'T', 'F', 'P', 'Px'}
    START_SYMBOL_NAME = 'E'

    def __init__(self):
        self._grammar = Grammar({
            'terminal_symbols': self.TERMINALS,
            'nonterminal_symbols': self.NONTERMINALS,
            'start_symbol': self.START_SYMBOL_NAME,
        })
        self.handlers = {
            'E -> E | T': self._handler_0,
            'E -> T': self._handler_1,
            'T -> T F': self._handler_2,
            'T -> F': self._handler_3,
            'F -> ( E )': self._handler_4,
            'F -> F *': self._handler_5,
            'F -> F +': self._handler_6,
            'F -> Fs': self._handler_7,
            'P -> .': self._handler_8,
            'P -> char': self._handler_9,
            'P -> char - char': self._handler_10,
            'Px -> Px P': self._handler_11,
            'Px -> P': self._handler_12,
            'F -> [ Px ]': self._handler_13,
            'F -> [ ^ Px ]': self._handler_14,
        }
        rules = []
        for rule_str, handler in self.handlers.items():
            rule = RegexProductionRule.from_string(rule_str, self._grammar.symbol_pool)
            rule.handler = handler
            rules.append(rule)
        self._grammar.init(rules)

    @staticmethod
    def _handler_0(nodes: List[NFA], children: List[Symbol]) -> NFA:
        raise NotImplementedError()

    @staticmethod
    def _handler_1(nodes: List[NFA], children: List[Symbol]) -> NFA:
        raise NotImplementedError()

    @staticmethod
    def _handler_2(nodes: List[NFA], children: List[Symbol]) -> NFA:
        raise NotImplementedError()

    @staticmethod
    def _handler_3(nodes: List[NFA], children: List[Symbol]) -> NFA:
        raise NotImplementedError()

    @staticmethod
    def _handler_4(nodes: List[NFA], children: List[Symbol]) -> NFA:
        raise NotImplementedError()

    @staticmethod
    def _handler_5(nodes: List[NFA], children: List[Symbol]) -> NFA:
        raise NotImplementedError()

    @staticmethod
    def _handler_6(nodes: List[NFA], children: List[Symbol]) -> NFA:
        raise NotImplementedError()

    @staticmethod
    def _handler_7(nodes: List[NFA], children: List[Symbol]) -> NFA:
        raise NotImplementedError()

    @staticmethod
    def _handler_8(nodes: List[NFA], children: List[Symbol]) -> NFA:
        raise NotImplementedError()

    @staticmethod
    def _handler_9(nodes: List[NFA], children: List[Symbol]) -> NFA:
        raise NotImplementedError()

    @staticmethod
    def _handler_10(nodes: List[NFA], children: List[Symbol]) -> NFA:
        raise NotImplementedError()

    @staticmethod
    def _handler_11(nodes: List[NFA], children: List[Symbol]) -> NFA:
        raise NotImplementedError()

    @staticmethod
    def _handler_12(nodes: List[NFA], children: List[Symbol]) -> NFA:
        raise NotImplementedError()

    @staticmethod
    def _handler_13(nodes: List[NFA], children: List[Symbol]) -> NFA:
        raise NotImplementedError()

    @staticmethod
    def _handler_14(nodes: List[NFA], children: List[Symbol]) -> NFA:
        raise NotImplementedError()

    def parse(self, regex: Regex) -> NFA:
        parse_table = self._grammar.parse_table
        symbols = regex.get_symbols(self._grammar.symbol_pool)
        start_symbol = self._grammar.start_symbol
        state_stack = [0]
        symbol_stack = []
        node_stack = []
        i = 0
        while True:
            state = state_stack[-1]
            symbol = symbols[i] if i < len(symbols) else self._grammar.symbol_pool.get_terminal(Grammar.END_SYMBOL_NAME)
            action = parse_table[state][symbol.abstract]
            if action == 'acc':
                return node_stack[-1]
            elif action[0] == 's':
                state_stack.append(int(action[1:]))
                symbol_stack.append(symbol)
                node_stack.append(NFA.from_symbol(symbol))
                i += 1
            elif action[0] == 'r':
                rule = self._grammar.rules[int(action[1:])]
                state_stack = state_stack[:-len(rule.right)]
                symbol_stack = symbol_stack[:-len(rule.right)]
                node_stack = node_stack[:-len(rule.right)]
                node_stack.append(rule._handler(node_stack, rule.right))
                state_stack.append(parse_table[state_stack[-1]][rule.left])
                symbol_stack.append(rule.left)
            else:
                raise ValueError(f'invalid action: {action}')
            if symbol in parse_table[state]:
                rule = parse_table[state][symbol]
                if rule.is_epsilon():
                    node_stack.append(NFA())
                    i += 1
                elif rule.is_terminal():
                    node_stack.append(NFA())
                    symbol_stack.append(symbol)
                    i += 1
                else:
                    state_stack.append(rule.right[0].id)
                    symbol_stack.append(symbol)
            else:
                if symbol_stack[-1] == symbol:
                    symbol_stack.pop()
                    node_stack.pop()
                    state_stack.pop()
                else:
                    raise ValueError(f'invalid symbol: {symbol}')
            if len(symbol_stack) == 0:
                break
        # i = 0
        # while i != len(symbols) - 1 or symbols[i].abstract != start_symbol:
