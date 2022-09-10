from typing import *

from ptree.symbol.symbol import AbstractSymbol, AbstractNonterminal, Symbol
from ptree.symbol.pool import SymbolPool
from ptree.lexer.fsm import FSMState, NFA
from ptree.parser.grammar import Grammar, ProductionRule, Transition


class Regex:

    def __init__(self, name: str, pattern: str):
        self.name = name
        self.pattern = pattern

    def get_symbols(self, symbol_pool: SymbolPool) -> List[Symbol]:
        symbols = []
        char_symbol = symbol_pool.get_terminal('char')
        i = 0
        while i < len(self.pattern):
            match c := self.pattern[i]:
                case '\\':
                    i += 1
                    if i >= len(self.pattern):
                        raise ValueError(f'invalid regex: {self.pattern}')
                    match c_ := self.pattern[i]:
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
        return f'{self.name} -> {self.pattern}'

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
            'T -> F': self._handler_1,
            'F -> ( E )': self._handler_3,
            'F -> F *': self._handler_4,
            'F -> F +': self._handler_5,
            'F -> P': self._handler_1,
            'P -> .': self._handler_6,
            'P -> char': self._handler_7,
            'P -> char - char': self._handler_8,
            'Px -> Px P': self._handler_9,
            'Px -> P': self._handler_1,
            'F -> [ Px ]': self._handler_3,
            'F -> [ ^ Px ]': self._handler_10,
        }
        rules = []
        for rule_str, handler in self.handlers.items():
            rule = RegexProductionRule.from_string(rule_str, self._grammar.symbol_pool)
            rule.handler = handler
            rules.append(rule)
        self._grammar.init(rules)

    @staticmethod
    def _handler_0(nodes: List[NFA], _) -> NFA:
        """
        E -> E | T
        """
        start, end = FSMState(), FSMState()
        start.add_transition(NFA.EPSILON, nodes[0].start)
        start.add_transition(NFA.EPSILON, nodes[2].start)
        for state in nodes[0].end:
            state.add_transition(NFA.EPSILON, end)
        for state in nodes[2].end:
            state.add_transition(NFA.EPSILON, end)
        nfa = NFA(start)
        nfa.end.add(end)
        return nfa

    @staticmethod
    def _handler_1(nodes: List[NFA], _) -> NFA:
        """
        E -> T;
        T -> F;
        F -> P;
        Px -> P;
        """
        return nodes[0]

    @staticmethod
    def _handler_2(nodes: List[NFA], _) -> NFA:
        """
        T -> T F
        """
        for state in nodes[0].end:
            state.add_transition(NFA.EPSILON, nodes[1].start)
        nfa = NFA(nodes[0].start)
        nfa.end = nodes[1].end
        return nfa

    @staticmethod
    def _handler_3(nodes: List[NFA], _) -> NFA:
        """
        F -> ( E )
        """
        return nodes[1]

    @staticmethod
    def _handler_4(nodes: List[NFA], _) -> NFA:
        """
        F -> F *
        """
        start, end = FSMState(), FSMState()
        start.add_transition(NFA.EPSILON, nodes[0].start)
        start.add_transition(NFA.EPSILON, end)
        for state in nodes[0].end:
            state.add_transition(NFA.EPSILON, nodes[0].start)
            state.add_transition(NFA.EPSILON, end)
        nfa = NFA(start)
        nfa.end.add(end)
        return nfa

    @staticmethod
    def _handler_5(nodes: List[NFA], _) -> NFA:
        """
        F -> F +
        """
        start, end = FSMState(), FSMState()
        start.add_transition(NFA.EPSILON, nodes[0].start)
        for state in nodes[0].end:
            state.add_transition(NFA.EPSILON, nodes[0].start)
            state.add_transition(NFA.EPSILON, end)
        nfa = NFA(start)
        nfa.end.add(end)
        return nfa

    @staticmethod
    def _handler_6(nodes: List[NFA], _) -> NFA:
        """
        P -> .
        """
        start = FSMState()
        for char in NFA.CHARSET:
            start.add_transition(char, nodes[0].start)
        nfa = NFA(start)
        nfa.end = nodes[0].end
        return nfa

    @staticmethod
    def _handler_7(nodes: List[NFA], children: List[Symbol]) -> NFA:
        """
        P -> char
        """
        start = FSMState()
        start.add_transition(children[0].value, nodes[0].start)
        nfa = NFA(start)
        nfa.end = nodes[0].end
        return nfa

    @staticmethod
    def _handler_8(nodes: List[NFA], children: List[Symbol]) -> NFA:
        """
        P -> char - char
        """
        start = FSMState()
        for char in range(ord(children[0].value), ord(children[2].value) + 1):
            start.add_transition(chr(char), nodes[0].start)
        nfa = NFA(start)
        nfa.end = nodes[0].end
        return nfa

    @staticmethod
    def _handler_9(nodes: List[NFA], _) -> NFA:
        """
        Px -> Px P
        """
        start, end = FSMState(), FSMState()
        start.add_transition(NFA.EPSILON, nodes[0].start)
        start.add_transition(NFA.EPSILON, nodes[1].start)
        for state in nodes[0].end:
            state.add_transition(NFA.EPSILON, end)
        for state in nodes[1].end:
            state.add_transition(NFA.EPSILON, end)
        nfa = NFA(start)
        nfa.end.add(end)
        return nfa

    @staticmethod
    def _handler_10(nodes: List[NFA], _) -> NFA:
        """
        F -> [ ^ Px ]
        """
        start = FSMState()
        for char in NFA.CHARSET - nodes[2].start.transitions.keys():
            start.add_transition(char, next(iter(next(iter(nodes[2].start.transitions.values())))))
        nfa = NFA(start)
        nfa.end = nodes[2].end
        return nfa

    def parse(self, regex: Regex) -> NFA:
        parse_table = self._grammar.parse_table
        symbols = regex.get_symbols(self._grammar.symbol_pool)
        state_stack = [0]
        symbol_stack = []
        node_stack = []
        i = 0
        while True:
            state = state_stack[-1]
            if i < len(symbols):
                symbol = symbols[i]
            else:
                symbol = Symbol(
                    Grammar.END_SYMBOL_NAME,
                    self._grammar.symbol_pool.get_terminal(Grammar.END_SYMBOL_NAME),
                )
            transition = parse_table.transitions[state].get(symbol.abstract, None)
            if transition is None:
                raise ValueError(f'invalid regular expression {regex.pattern} for {regex.name}')
            if transition.type == Transition.TYPE_SHIFT:
                node_stack.append(NFA())
                symbol_stack.append(symbol)
                state_stack.append(transition.target)
                i += 1
            elif transition.type == Transition.TYPE_GOTO:
                state_stack.append(transition.target)
                i += 1
            elif transition.type == Transition.TYPE_REDUCE:
                rule = transition.target
                right_length = len(rule.right)
                children, symbol_stack = symbol_stack[-right_length:], symbol_stack[:-right_length]
                nodes, node_stack = node_stack[-right_length:], node_stack[:-right_length]
                state_stack = state_stack[:-right_length]
                node_stack.append(rule.handler(nodes, children))
                symbol_stack.append(Symbol(rule.left.name, rule.left))
                i -= 1
                symbols[i] = symbol_stack[-1]
            else:
                break
        dfa = node_stack[0]
        for state in dfa.end:
            state.accept_list.append(regex.name)
        return dfa
