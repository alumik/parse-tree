import fire

import ptree

from typing import *

from ptree.lexer.regex import Regex, RegexEngine


def match(pattern: str, text: str) -> Optional[int]:
    regex = Regex(pattern, pattern)
    engine = RegexEngine()
    nfa = engine.parse(regex)
    ptree.render(nfa, directory='out', name='nfa', output_format='svg')
    dfa = nfa.to_dfa()
    ptree.render(ptree, directory='out', name='dfa', output_format='svg')
    return dfa.match(text)


if __name__ == '__main__':
    fire.Fire(match)
