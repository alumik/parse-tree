import fire

from typing import *

from ptree.lexer.regex import Regex, RegexEngine


def match(pattern: str = '(a|b)*abb', text: str = 'aabbefg') -> Optional[int]:
    regex = Regex(pattern, pattern)
    engine = RegexEngine()
    dfa = engine.parse(regex).to_dfa()
    dfa.render(directory='out', name='dfa', output_format='svg')
    return dfa.match(text)


if __name__ == '__main__':
    fire.Fire(match)
