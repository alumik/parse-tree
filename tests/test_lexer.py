import ptree

from ptree.lexer.regex import Regex, RegexEngine


def main():
    config = ptree.load_config('config-2.yaml')
    parser = ptree.Parser(config)
    # lexer = ptree.Lexer(config, parser=parser)
    regex_engine = RegexEngine()
    regex = Regex('identifier', r'[a-zA-Z_][a-zA-Z0-9_]*')
    print(regex.get_symbols(regex_engine._grammar.symbol_pool))


if __name__ == '__main__':
    main()
