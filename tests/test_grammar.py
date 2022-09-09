import ptree

from ptree.parser.grammar import Grammar


def main():
    config = ptree.load_config('config-2.yaml')
    grammar = Grammar(config)
    grammar.init()
    print(grammar.parse_table)


if __name__ == '__main__':
    main()
