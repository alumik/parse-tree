import fire

import ptree


def main(config: str = 'config.yaml', text: str = 'abababab'):
    config = ptree.load_config(config)
    grammar = ptree.Grammar(config)
    grammar.init()
    lexer = ptree.Lexer(config, symbol_pool=grammar.symbol_pool)
    parser = ptree.Parser(grammar)
    print('parse table:')
    print(grammar.parse_table)

    tokens = lexer.tokenize(text)
    print('tokens:')
    ptree.pretty_print_tokens(tokens)

    parse_tree = parser.parse(tokens)
    parse_tree.render(directory='out', name='parse-tree', output_format='svg')


if __name__ == '__main__':
    fire.Fire(main)
