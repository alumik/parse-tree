import unittest

import ptree

from ptree.parser.grammar import Grammar


class TestGrammar(unittest.TestCase):

    def test_first_set(self):
        config = ptree.load_config('configs/test-grammar-test-first-set.yaml')
        grammar = Grammar(config)
        grammar.init()
        symbol_pool = grammar.symbol_pool

        symbol_a = symbol_pool.get_terminal('a')
        symbol_b = symbol_pool.get_terminal('b')
        symbol_c = symbol_pool.get_terminal('c')
        symbol_d = symbol_pool.get_terminal('d')
        symbol_g = symbol_pool.get_terminal('g')
        symbol_null = symbol_pool.get_terminal(Grammar.NULL_SYMBOL_NAME)

        first_set = {
            'A': {symbol_a, symbol_b, symbol_c, symbol_d, symbol_g},
            'B': {symbol_b, symbol_null},
            'C': {symbol_a, symbol_c, symbol_d},
            'D': {symbol_d, symbol_null},
            '_S': {symbol_a, symbol_b, symbol_c, symbol_d, symbol_g},
            'E': {symbol_c, symbol_g},
        }

        for symbol in grammar.symbol_pool.get_nonterminals():
            self.assertEqual(symbol.first, first_set[symbol.name])

    def test_parse_table(self):
        config = ptree.load_config('configs/test-grammar-test-parse-table.yaml')
        grammar = Grammar(config)
        grammar.init()
        ptree.pprint(grammar.parse_table)


if __name__ == '__main__':
    unittest.main()
