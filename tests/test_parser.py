import unittest

import ptree


class TestParser(unittest.TestCase):

    def test_equation(self):
        config = ptree.load_config('configs/test-parser-test-equation.yaml')
        grammar = ptree.Grammar(config)
        grammar.init()
        lexer = ptree.Lexer(config, symbol_pool=grammar.symbol_pool)
        parser = ptree.Parser(grammar)
        tokens = lexer.tokenize('3*(6+(4/2)-5)+8')
        parse_tree = parser.parse(tokens)
        parse_tree.render(directory='out', name='test-parser-test-equation-parse-tree', output_format='svg')
