import ptree


def main():
    config = ptree.load_config('config.yaml')
    parser = ptree.Parser(config)
    lexer = ptree.Lexer(config, parser=parser)
    parse_tree = parser.parse(lexer.tokenize(input()))
    ptree.plot(parse_tree, save_path='parse_tree.png')


if __name__ == '__main__':
    main()
