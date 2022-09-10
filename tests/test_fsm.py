import unittest

from ptree.lexer.fsm import FSMState, NFA


class TestFSM(unittest.TestCase):

    def test_nfa_to_dfa(self):
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
        nfa.render(directory='out', name='test_nfa_to_nfa_nfa', output_format='svg')

        dfa = nfa.to_dfa()
        dfa.render(directory='out', name='test_nfa_to_nfa_dfa', output_format='svg')

        self.assertEqual(dfa.match('abdsffgabb'), None)
        self.assertEqual(dfa.match('abab'), None)
        self.assertEqual(dfa.match('abbbababbabb'), ('(a|b)*abb', 12))
        self.assertEqual(dfa.match('abb'), ('(a|b)*abb', 3))
        self.assertEqual(dfa.match('abbabb'), ('(a|b)*abb', 6))
        self.assertEqual(dfa.match('aabbefg'), ('(a|b)*abb', 4))

    def test_merge_fsm(self):
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
        nfa.render(directory='out', name='test_merge_fsm_nfa', output_format='svg')

        dfa = nfa.to_dfa()
        dfa.render(directory='out', name='test_merge_fsm_dfa', output_format='svg')

        self.assertEqual(dfa.match('abb'), ('a*b+', 3))
        self.assertEqual(dfa.match('abbb'), ('a*b+', 4))
        self.assertEqual(dfa.match('aefg'), ('a', 1))
        self.assertEqual(dfa.match('efg'), None)


if __name__ == '__main__':
    unittest.main()
