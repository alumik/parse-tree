import pathlib

from typing import *

from ptree.utils import escaper


class FSMState:

    def __init__(self):
        self.transitions = {}
        self.accept_list = []

    def add_transition(self, on: str, target: 'FSMState'):
        self.transitions.setdefault(on, set()).add(target)

    def get_one_target(self, on: str) -> Optional['FSMState']:
        return next(iter(self.get_targets(on)), None)

    def get_targets(self, on: str) -> Set['FSMState']:
        return self.transitions.get(on, set())

    def dfs(self,
            visited: Optional[List['FSMState']] = None,
            action: Callable[['FSMState'], None] = lambda _: None) -> List['FSMState']:
        action(self)
        if visited is None:
            visited = []
        visited.append(self)
        for targets in self.transitions.values():
            for target in targets:
                if target not in visited:
                    target.dfs(visited, action)
        return visited


class NFA:
    EPSILON = '\0'
    CHARSET = set(chr(i + 1) for i in range(128)) - {'\r', '\n'}

    def __init__(self, start: Optional[FSMState] = None, end: Optional[Set[FSMState]] = None):
        self.start = start
        self.end = end or set()
        if self.start is None:
            self.start = FSMState()
            self.end.add(self.start)

    @classmethod
    def union(cls, others: List['NFA']) -> 'NFA':
        start = FSMState()
        for nfa in others:
            start.add_transition(NFA.EPSILON, nfa.start)
        return cls(start)

    def to_dfa(self) -> 'DFA':
        return DFA(self.start)

    def render(self,
               directory: Union[pathlib.Path, str] = '',
               name: str = 'out',
               output_format: str = 'svg'):
        import graphviz
        dot = graphviz.Digraph(format=output_format, graph_attr={'rankdir': 'LR'})
        states = self.start.dfs()
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
        dot.edge('0', str(state_id_map[self.start]), label='start')
        dot.render(str(pathlib.Path(directory) / name))


class DFA(NFA):

    def __init__(self, start: Optional[FSMState] = None):
        super().__init__(start)
        start_closure = self._get_closure({start})
        self.start = FSMState()
        self.start.accept_list = list({accept for nfa_state in start_closure for accept in nfa_state.accept_list})
        state_map = {frozenset(start_closure): self.start}
        state_queue = [start_closure]
        while state_queue:
            closure = state_queue.pop()
            dfa_state = state_map[frozenset(closure)]
            for on in {on for nfa_state in closure for on in nfa_state.transitions if on != NFA.EPSILON}:
                targets = set()
                for nfa_state in closure:
                    targets.update(nfa_state.get_targets(on))
                target_closure = self._get_closure(targets)
                if frozenset(target_closure) not in state_map:
                    target_state = FSMState()
                    target_state.accept_list = list(
                        {accept for nfa_state in target_closure for accept in nfa_state.accept_list})
                    state_map[frozenset(target_closure)] = target_state
                    state_queue.append(target_closure)
                else:
                    target_state = state_map[frozenset(target_closure)]
                dfa_state.add_transition(on, target_state)

    @staticmethod
    def _get_closure(closure: Set[FSMState]) -> Set[FSMState]:
        state_queue = list(closure)
        while state_queue:
            state = state_queue.pop()
            for target in state.get_targets(NFA.EPSILON):
                if target not in closure:
                    closure.add(target)
                    state_queue.append(target)
        return closure

    @classmethod
    def union(cls, others: List['DFA']) -> 'DFA':
        nfa = super().union(others)
        return DFA(nfa.start)

    def to_dfa(self) -> 'DFA':
        return self

    def match(self, text: str) -> Optional[Tuple[str, int]]:
        state = self.start
        end_state, end_index = None, 0
        for i, c in enumerate(text):
            target = state.get_one_target(c)
            if target is None:
                break
            state = target
            if state.accept_list:
                end_state, end_index = state, i + 1
        if end_state is None:
            return None
        return end_state.accept_list[0], end_index
