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
    s8 = FSMState()
    s9 = FSMState()
    s10 = FSMState()

    s0.add_transition(NFA.EPSILON, s1)
    s1.add_transition(NFA.EPSILON, s5)
    s1.add_transition(NFA.EPSILON, s6)
    s5.add_transition('a', s2)
    s6.add_transition('b', s3)
    s2.add_transition(NFA.EPSILON, s4)
    s3.add_transition(NFA.EPSILON, s4)
    s4.add_transition(NFA.EPSILON, s7)
    s7.add_transition('a', s8)
    s8.add_transition('b', s9)
    s9.add_transition('b', s10)
    s0.add_transition(NFA.EPSILON, s7)
    s4.add_transition(NFA.EPSILON, s1)

    s10.accept_list = ['(a|b)*abb']
    nfa = NFA(['(a|b)*abb'], s0)
    nfa.render(directory='out', name='test_nfa_nfa', output_format='svg')

    dfa = nfa.to_dfa()
    dfa.render(directory='out', name='test_nfa_dfa', output_format='svg')

    print(dfa.match("abdsffgabb"))
    print(dfa.match("abab"))
    print(dfa.match("abbbababbabb"))
    print(dfa.match("abb"))
    print(dfa.match("abbabb"))
    print(dfa.match("aabbefg"))


if __name__ == '__main__':
    main()
