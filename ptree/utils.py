import yaml
import pathlib

from typing import Any

from ptree.symbol.symbol import Token
from ptree.lexer.fsm import NFA
from ptree.parser.grammar import Transition, ParseTable, Grammar
from ptree.parser.parser import ParseTree


def load_config(path: str) -> dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def escaper(s: str) -> str:
    return s \
        .replace('\\', '\\\\') \
        .replace('\r', '\\\\r') \
        .replace('\n', '\\\\n') \
        .replace('\t', '\\\\t') \
        .replace('\f', '\\\\f')


def pprint(obj):
    from dashtable import data2rst
    if isinstance(obj, list) and all(isinstance(x, Token) for x in obj):
        table = [['', 'SYMBOL', 'VALUE']]
        for i, token in enumerate(obj):
            table.append([str(i + 1), token.symbol.name, token.value])
        print(data2rst(table))
    elif isinstance(obj, ParseTable):
        terminals = list(obj.config['terminal_symbols'])
        nonterminals = list(obj.config['nonterminal_symbols'])
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
        for state, state_id in obj.state_id_map.items():
            row = [state_id]
            for name in terminals + nonterminals:
                symbol = obj.symbol_pool.get_symbol(name)
                if symbol in obj.transitions[state_id]:
                    transition = obj.transitions[state_id][symbol]
                    if transition.type == Transition.TYPE_SHIFT:
                        row.append(f's{transition.target}')
                    elif transition.type == Transition.TYPE_REDUCE:
                        row.append(f'r{transition.target.id}')
                    elif transition.type == Transition.TYPE_ACCEPT:
                        row.append('acc')
                    else:
                        row.append(f'{transition.target}')
                else:
                    row.append('')
            row.append(str(state))
            table.append(row)
        action_span = [[0, i + 1] for i in range(len(terminals))]
        goto_span = [[0, i + 1] for i in range(len(terminals), len(terminals) + len(nonterminals))]
        print(data2rst(table, spans=[action_span, goto_span]))
    else:
        print(obj)


def render(obj,
           directory: pathlib.Path | str = '',
           name: str = 'out',
           output_format: str = 'svg') -> str:
    import graphviz
    if isinstance(obj, NFA):
        dot = graphviz.Digraph(format=output_format, graph_attr={'rankdir': 'LR'})
        states = obj.start.dfs()
        state_id_map = {state: i + 1 for i, state in enumerate(states)}
        for state in states:
            shape = 'circle'
            if state.accept_list:
                shape = 'doublecircle'
                dot.node(
                    f'accept list {state_id_map[state]}',
                    label='\n'.join(state.accept_list),
                    shape='rectangle',
                    color='blue',
                )
                dot.edge(
                    f'{state_id_map[state]}',
                    f'accept list {state_id_map[state]}',
                    style='dashed',
                    color='blue',
                    arrowhead='none',
                )
            dot.node(str(state_id_map[state]), shape=shape)
        for state in states:
            for on, targets in state.transitions.items():
                for target in targets:
                    dot.edge(
                        str(state_id_map[state]),
                        str(state_id_map[target]),
                        label=escaper(on) if on != NFA.EPSILON else 'ε',
                    )
        dot.node('0', shape='point')
        dot.edge('0', str(state_id_map[obj.start]), label='start')
        dot.render(str(pathlib.Path(directory) / name))
        return dot.source
    elif isinstance(obj, ParseTree):
        dot = graphviz.Digraph(format=output_format, graph_attr={'rankdir': 'TB'})
        node_id_map = {obj: 0}
        node_queue = [obj]
        while node_queue:
            node = node_queue.pop()
            dot.node(str(node_id_map[node]), label=escaper(node.token.symbol.name))
            if not node.children:
                dot.node(f'v{node_id_map[node]}', label=escaper(node.token.value), shape='box', color='blue')
                dot.edge(
                    str(node_id_map[node]),
                    f'v{node_id_map[node]}',
                    style='dashed',
                    color='blue',
                    arrowhead='none',
                )
            for child in node.children:
                if child not in node_id_map:
                    node_id_map[child] = len(node_id_map)
                    node_queue.append(child)
                dot.edge(str(node_id_map[node]), str(node_id_map[child]))
        dot.render(str(pathlib.Path(directory) / name))
        return dot.source
    else:
        raise TypeError(f'cannot render object of type {type(obj)}')
