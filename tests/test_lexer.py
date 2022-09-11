import unittest

import ptree

from ptree.symbol.symbol import Symbol


class TestLexer(unittest.TestCase):

    def test_ab(self):
        config = ptree.load_config('configs/test-lexer-test-ab.yaml')
        grammar = ptree.Grammar(config)
        lexer = ptree.Lexer(config, symbol_pool=grammar.symbol_pool)
        lexer._dfa.render(directory='out', name='test-lexer-test-ab-dfa', output_format='svg')
        result = lexer.tokenize('aabaabc abaab')
        self.assertEqual(Symbol('ab', grammar.symbol_pool.get_terminal('AB2')), result[0])
        self.assertEqual(Symbol('abc', grammar.symbol_pool.get_terminal('ABC')), result[1])
        self.assertEqual(Symbol('ab', grammar.symbol_pool.get_terminal('AB2')), result[2])
        self.assertEqual(Symbol('ab', grammar.symbol_pool.get_terminal('AB2')), result[3])

    def test_cpp(self):
        config = ptree.load_config('configs/test-lexer-test-cpp.yaml')
        grammar = ptree.Grammar(config)
        lexer = ptree.Lexer(config, symbol_pool=grammar.symbol_pool)
        tokens = lexer.tokenize('''int main() {int a = a + 1; cout << a << endl; return 0;}''')
        ground_truth = [
            Symbol('int', grammar.symbol_pool.get_terminal('KEYWORD')),
            Symbol('main', grammar.symbol_pool.get_terminal('IDENTIFIER')),
            Symbol('(', grammar.symbol_pool.get_terminal('LP')),
            Symbol(')', grammar.symbol_pool.get_terminal('RP')),
            Symbol('{', grammar.symbol_pool.get_terminal('LB')),
            Symbol('int', grammar.symbol_pool.get_terminal('KEYWORD')),
            Symbol('a', grammar.symbol_pool.get_terminal('IDENTIFIER')),
            Symbol('=', grammar.symbol_pool.get_terminal('ASSIGN_OP')),
            Symbol('a', grammar.symbol_pool.get_terminal('IDENTIFIER')),
            Symbol('+', grammar.symbol_pool.get_terminal('ADD_OP')),
            Symbol('1', grammar.symbol_pool.get_terminal('INTEGER')),
            Symbol(';', grammar.symbol_pool.get_terminal('SEMICOLON')),
            Symbol('cout', grammar.symbol_pool.get_terminal('IDENTIFIER')),
            Symbol('<<', grammar.symbol_pool.get_terminal('LSTREAM')),
            Symbol('a', grammar.symbol_pool.get_terminal('IDENTIFIER')),
            Symbol('<<', grammar.symbol_pool.get_terminal('LSTREAM')),
            Symbol('endl', grammar.symbol_pool.get_terminal('IDENTIFIER')),
            Symbol(';', grammar.symbol_pool.get_terminal('SEMICOLON')),
            Symbol('return', grammar.symbol_pool.get_terminal('KEYWORD')),
            Symbol('0', grammar.symbol_pool.get_terminal('INTEGER')),
            Symbol(';', grammar.symbol_pool.get_terminal('SEMICOLON')),
            Symbol('}', grammar.symbol_pool.get_terminal('RB')),
        ]
        self.assertEqual(ground_truth, tokens)
