import unittest

import ptree

from ptree.symbol.symbol import Token


class TestLexer(unittest.TestCase):

    def test_ab(self):
        config = ptree.load_config('configs/test-lexer-test-ab.yaml')
        grammar = ptree.Grammar(config)
        lexer = ptree.Lexer(config, symbol_pool=grammar.symbol_pool)
        lexer._dfa.render(directory='out', name='test-lexer-test-ab-dfa', output_format='svg')
        result = lexer.tokenize('aabaabc abaab')
        self.assertEqual(Token('ab', grammar.symbol_pool.get_terminal('AB2')), result[0])
        self.assertEqual(Token('abc', grammar.symbol_pool.get_terminal('ABC')), result[1])
        self.assertEqual(Token('ab', grammar.symbol_pool.get_terminal('AB2')), result[2])
        self.assertEqual(Token('ab', grammar.symbol_pool.get_terminal('AB2')), result[3])

    def test_cpp(self):
        config = ptree.load_config('configs/test-lexer-test-cpp.yaml')
        grammar = ptree.Grammar(config)
        lexer = ptree.Lexer(config, symbol_pool=grammar.symbol_pool)
        tokens = lexer.tokenize('''int main() {int a = a + 1; cout << a << endl; return 0;}''')
        ground_truth = [
            Token('int', grammar.symbol_pool.get_terminal('KEYWORD')),
            Token('main', grammar.symbol_pool.get_terminal('IDENTIFIER')),
            Token('(', grammar.symbol_pool.get_terminal('LP')),
            Token(')', grammar.symbol_pool.get_terminal('RP')),
            Token('{', grammar.symbol_pool.get_terminal('LB')),
            Token('int', grammar.symbol_pool.get_terminal('KEYWORD')),
            Token('a', grammar.symbol_pool.get_terminal('IDENTIFIER')),
            Token('=', grammar.symbol_pool.get_terminal('ASSIGN_OP')),
            Token('a', grammar.symbol_pool.get_terminal('IDENTIFIER')),
            Token('+', grammar.symbol_pool.get_terminal('ADD_OP')),
            Token('1', grammar.symbol_pool.get_terminal('INTEGER')),
            Token(';', grammar.symbol_pool.get_terminal('SEMICOLON')),
            Token('cout', grammar.symbol_pool.get_terminal('IDENTIFIER')),
            Token('<<', grammar.symbol_pool.get_terminal('LSTREAM')),
            Token('a', grammar.symbol_pool.get_terminal('IDENTIFIER')),
            Token('<<', grammar.symbol_pool.get_terminal('LSTREAM')),
            Token('endl', grammar.symbol_pool.get_terminal('IDENTIFIER')),
            Token(';', grammar.symbol_pool.get_terminal('SEMICOLON')),
            Token('return', grammar.symbol_pool.get_terminal('KEYWORD')),
            Token('0', grammar.symbol_pool.get_terminal('INTEGER')),
            Token(';', grammar.symbol_pool.get_terminal('SEMICOLON')),
            Token('}', grammar.symbol_pool.get_terminal('RB')),
        ]
        self.assertEqual(ground_truth, tokens)
