from typing import *

from ptree.symbol.symbol import Token
from ptree.parser.grammar import Grammar, Transition


class ParseTree:

    def __init__(self, token: Token, children: Optional[List['ParseTree']] = None):
        self.token = token
        self.children = children or []


class Parser:

    def __init__(self, grammar: Grammar):
        self._grammar = grammar

    def parse(self, tokens: List[Token]) -> ParseTree:
        parse_table = self._grammar.parse_table
        state_stack = [0]
        node_stack = []
        i = 0
        while True:
            state = state_stack[-1]
            if i < len(tokens):
                token = tokens[i]
            else:
                token = Token(
                    value=Grammar.END_SYMBOL_NAME,
                    symbol=self._grammar.symbol_pool.get_terminal(Grammar.END_SYMBOL_NAME),
                )
            transition = parse_table.transitions[state].get(token.symbol, None)
            if transition is None:
                raise ValueError(f'unexpected token {token.symbol.name}: {token.value} at index {i}')
            if transition.type == Transition.TYPE_SHIFT:
                state_stack.append(transition.target)
                node_stack.append(ParseTree(token))
                i += 1
            elif transition.type == Transition.TYPE_GOTO:
                state_stack.append(transition.target)
                i += 1
            elif transition.type == Transition.TYPE_REDUCE:
                rule = transition.target
                rule_length = len(rule.right)
                children, node_stack = node_stack[-rule_length:], node_stack[:-rule_length]
                node = ParseTree(token=Token(value=rule.left.name, symbol=rule.left), children=children)
                node_stack.append(node)
                state_stack = state_stack[:-rule_length]
                i -= 1
                tokens[i] = node.token
            else:
                return ParseTree(
                    token=Token(
                        value=Grammar.START_SYMBOL_NAME,
                        symbol=self._grammar.symbol_pool.get_nonterminal(Grammar.START_SYMBOL_NAME)
                    ),
                    children=node_stack,
                )
