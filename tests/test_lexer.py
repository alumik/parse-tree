import unittest

import ptree

from ptree.symbol.symbol import Symbol


class TestLexer(unittest.TestCase):

    def test_lexer(self):
        config = ptree.load_config('configs/test_lexer_test_lexer.yaml')
        grammar = ptree.Grammar(config)
        lexer = ptree.Lexer(config, symbol_pool=grammar.symbol_pool)
        lexer._dfa.render(directory='out', name='test_lexer_dfa', output_format='svg')
        result = lexer.tokenize('aabaabc abaab')
        self.assertEqual(Symbol('ab', grammar.symbol_pool.get_terminal('AB2')), result[0])
        self.assertEqual(Symbol('abc', grammar.symbol_pool.get_terminal('ABC')), result[1])
        self.assertEqual(Symbol('ab', grammar.symbol_pool.get_terminal('AB2')), result[2])
        self.assertEqual(Symbol('ab', grammar.symbol_pool.get_terminal('AB2')), result[3])
