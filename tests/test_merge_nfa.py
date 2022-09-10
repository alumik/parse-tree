from ptree.lexer.fsm import FSMState, NFA


def main():
    s0 = FSMState()
    s1 = FSMState()
    s2 = FSMState()
    s3 = FSMState()
    s4 = FSMState()
    s5 = FSMState()
    s6 = FSMState()
    s7 = FSMState()

    s0.add_transition('a', s0)
    s0.add_transition('b', s1)
    s1.add_transition('b', s1)
    s1.accept_list = ['a*b+']
    nfa0 = NFA(['a*b+'], s0)

    s2.add_transition('a', s3)
    s3.accept_list = ['a']
    nfa1 = NFA(['a'], s2)

    s4.add_transition('a', s5)
    s5.add_transition('b', s6)
    s6.add_transition('b', s7)
    s7.accept_list = ['abb']
    nfa2 = NFA(['abb'], s4)

    nfa = NFA.union([nfa0, nfa1, nfa2])
    nfa.render(directory='out', name='test_merge_nfa_nfa', output_format='svg')

    dfa = nfa.to_dfa()
    dfa.render(directory='out', name='test_merge_nfa_dfa', output_format='svg')


if __name__ == '__main__':
    main()
