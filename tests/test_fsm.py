import unittest

import ptree

from ptree.lexer.fsm import FSMState, NFA
from ptree.lexer.regex import Regex, RegexEngine


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
        nfa = NFA(s0)
        ptree.render(nfa, directory='out', name='test-nfa-to-dfa-nfa', output_format='svg')

        dfa = nfa.to_dfa()
        ptree.render(nfa, directory='out', name='test-nfa-to-dfa-dfa', output_format='svg')

        self.assertEqual(None, dfa.match('abdsffgabb'))
        self.assertEqual(None, dfa.match('abab'))
        self.assertEqual(('(a|b)*abb', 12), dfa.match('abbbababbabb'))
        self.assertEqual(('(a|b)*abb', 3), dfa.match('abb'))
        self.assertEqual(('(a|b)*abb', 6), dfa.match('abbabb'))
        self.assertEqual(('(a|b)*abb', 4), dfa.match('aabbefg'))

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
        nfa0 = NFA(s0)
        ptree.render(nfa0, directory='out', name='test-merge-fsm-nfa0', output_format='svg')

        s2.add_transition('a', s3)
        s3.accept_list = ['a']
        nfa1 = NFA(s2)
        ptree.render(nfa1, directory='out', name='test-merge-fsm-nfa1', output_format='svg')

        s4.add_transition('a', s5)
        s5.add_transition('b', s6)
        s6.add_transition('b', s7)
        s7.accept_list = ['abb']
        nfa2 = NFA(s4)
        ptree.render(nfa2, directory='out', name='test-merge-fsm-nfa2', output_format='svg')

        nfa = NFA.union([nfa0, nfa1, nfa2])
        ptree.render(nfa, directory='out', name='test-merge-fsm-nfa', output_format='svg')

        dfa = nfa.to_dfa()
        ptree.render(dfa, directory='out', name='test-merge-fsm-dfa', output_format='svg')

        self.assertIn(dfa.match('abb'), [('a*b+', 3), ('abb', 3)])
        self.assertEqual(('a*b+', 4), dfa.match('abbb'))
        self.assertEqual(('a', 1), dfa.match('aefg'))
        self.assertEqual(None, (dfa.match('efg')))

    def test_parse_regex(self):
        pattern = 'a+[bcd]ef*[g-j]k+'
        regex = Regex(pattern, pattern)
        engine = RegexEngine()
        nfa = engine.parse(regex)
        ptree.render(nfa, directory='out', name='test-parse-regex-nfa', output_format='svg')
        dfa = nfa.to_dfa()
        ptree.render(dfa, directory='out', name='test-parse-regex-dfa', output_format='svg')
        self.assertEqual(('a+[bcd]ef*[g-j]k+', 5), dfa.match('acehkd'))


if __name__ == '__main__':
    unittest.main()
