import fire

import ptree


def main(config: str, text: str):
    config = ptree.load_config(config)
    grammar = ptree.Grammar(config)
    grammar.init()

    # Output 1: grammar
    print('parse table:')
    ptree.pprint(grammar.parse_table)

    lexer = ptree.Lexer(config=config, symbol_pool=grammar.symbol_pool)
    parser = ptree.Parser(grammar)
    tokens = lexer.tokenize(text)

    # Output 2: tokens
    print('tokens:')
    ptree.pprint(tokens)

    parse_tree = parser.parse(tokens)

    # Output 3: parse tree
    print('parse tree:')
    dot_source = ptree.render(parse_tree, directory='out', name='parse-tree', output_format='svg')
    print(dot_source)


if __name__ == '__main__':
    fire.Fire(main)
