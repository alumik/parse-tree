import pathlib

from typing import *

from ptree.utils import escaper
from ptree.symbol.symbol import Symbol
from ptree.parser.grammar import Grammar, Transition


class ParseTree:

    def __init__(self, symbol: Symbol, children: Optional[List['ParseTree']] = None):
        self.symbol = symbol
        self.children = children or []

    def render(self,
               directory: Union[pathlib.Path, str] = '',
               name: str = 'out',
               output_format: str = 'svg',
               view: bool = False):
        import graphviz
        dot = graphviz.Digraph(format=output_format, graph_attr={'rankdir': 'TB'})
        node_id_map = {self: 0}
        node_queue = [self]
        while node_queue:
            node = node_queue.pop()
            dot.node(str(node_id_map[node]), label=escaper(node.symbol.abstract.name))
            if not node.children:
                dot.node(f'value {node_id_map[node]}', label=escaper(node.symbol.value), shape='box', color='blue')
                dot.edge(
                    str(node_id_map[node]),
                    f'value {node_id_map[node]}',
                    style='dashed',
                    color='blue',
                    arrowhead='none',
                )
            for child in node.children:
                if child not in node_id_map:
                    node_id_map[child] = len(node_id_map)
                    node_queue.append(child)
                dot.edge(str(node_id_map[node]), str(node_id_map[child]))
        dot.render(str(pathlib.Path(directory) / name), view=view)


class Parser:

    def __init__(self, grammar: Grammar):
        self._grammar = grammar
        self._grammar.init()

    def parse(self, tokens: List[Symbol]) -> ParseTree:
        parse_table = self._grammar.parse_table
        state_stack = [0]
        node_stack = []
        i = 0
        while True:
            state = state_stack[-1]
            if i < len(tokens):
                token = tokens[i]
            else:
                token = Symbol(
                    Grammar.END_SYMBOL_NAME,
                    self._grammar.symbol_pool.get_terminal(Grammar.END_SYMBOL_NAME),
                )
            transition = parse_table.transitions[state].get(token.abstract, None)
            if transition is None:
                raise ValueError(f'unexpected token {token.abstract.name}: {token.value} at {i}')
            if transition.type == Transition.TYPE_SHIFT:
                node_stack.append(ParseTree(token))
                state_stack.append(transition.target)
                i += 1
            elif transition.type == Transition.TYPE_GOTO:
                state_stack.append(transition.target)
                i += 1
            elif transition.type == Transition.TYPE_REDUCE:
                rule = transition.target
                right_length = len(rule.right)
                children, node_stack = node_stack[-right_length:], node_stack[:-right_length]
                state_stack = state_stack[:-right_length]
                node = ParseTree(Symbol(rule.left.name, rule.left), children)
                node_stack.append(node)
                i -= 1
                tokens[i] = node.symbol
            else:
                return ParseTree(
                    Symbol(
                        Grammar.START_SYMBOL_NAME,
                        self._grammar.symbol_pool.get_nonterminal(Grammar.START_SYMBOL_NAME)
                    ),
                    node_stack,
                )
