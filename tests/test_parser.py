import unittest

import ptree


class TestParser(unittest.TestCase):

    def _assertDotEqual(self, expected, actual):
        expected = [line.strip() for line in expected.splitlines() if line.strip()]
        actual = [line.strip() for line in actual.splitlines() if line.strip()]
        self.assertEqual(expected, actual)

    def test_equation(self):
        config = ptree.load_config('configs/test-parser-test-equation.yaml')
        grammar = ptree.Grammar(config)
        grammar.init()
        lexer = ptree.Lexer(config, symbol_pool=grammar.symbol_pool)
        parser = ptree.Parser(grammar)
        tokens = lexer.tokenize('3*(6+(4/2)-5)+8')
        parse_tree = parser.parse(tokens)
        dot_source = ptree.render(
            parse_tree,
            directory='out',
            name='test-parser-test-equation-parse-tree',
            output_format='svg',
        )
        self._assertDotEqual(
            """
            digraph {
                graph [rankdir=TB]
                0 [label=_S]
                0 -> 1
                1 [label=E]
                1 -> 2
                1 -> 3
                1 -> 4
                4 [label=T]
                4 -> 5
                5 [label=F]
                5 -> 6
                6 [label=num]
                v6 [label=8 color=blue shape=box]
                6 -> v6 [arrowhead=none color=blue style=dashed]
                3 [label="+"]
                v3 [label="+" color=blue shape=box]
                3 -> v3 [arrowhead=none color=blue style=dashed]
                2 [label=E]
                2 -> 7
                7 [label=T]
                7 -> 8
                7 -> 9
                7 -> 10
                10 [label=F]
                10 -> 11
                10 -> 12
                10 -> 13
                13 [label=")"]
                v13 [label=")" color=blue shape=box]
                13 -> v13 [arrowhead=none color=blue style=dashed]
                12 [label=E]
                12 -> 14
                12 -> 15
                12 -> 16
                16 [label=T]
                16 -> 17
                17 [label=F]
                17 -> 18
                18 [label=num]
                v18 [label=5 color=blue shape=box]
                18 -> v18 [arrowhead=none color=blue style=dashed]
                15 [label="-"]
                v15 [label="-" color=blue shape=box]
                15 -> v15 [arrowhead=none color=blue style=dashed]
                14 [label=E]
                14 -> 19
                14 -> 20
                14 -> 21
                21 [label=T]
                21 -> 22
                22 [label=F]
                22 -> 23
                22 -> 24
                22 -> 25
                25 [label=")"]
                v25 [label=")" color=blue shape=box]
                25 -> v25 [arrowhead=none color=blue style=dashed]
                24 [label=E]
                24 -> 26
                26 [label=T]
                26 -> 27
                26 -> 28
                26 -> 29
                29 [label=F]
                29 -> 30
                30 [label=num]
                v30 [label=2 color=blue shape=box]
                30 -> v30 [arrowhead=none color=blue style=dashed]
                28 [label="/"]
                v28 [label="/" color=blue shape=box]
                28 -> v28 [arrowhead=none color=blue style=dashed]
                27 [label=T]
                27 -> 31
                31 [label=F]
                31 -> 32
                32 [label=num]
                v32 [label=4 color=blue shape=box]
                32 -> v32 [arrowhead=none color=blue style=dashed]
                23 [label="("]
                v23 [label="(" color=blue shape=box]
                23 -> v23 [arrowhead=none color=blue style=dashed]
                20 [label="+"]
                v20 [label="+" color=blue shape=box]
                20 -> v20 [arrowhead=none color=blue style=dashed]
                19 [label=E]
                19 -> 33
                33 [label=T]
                33 -> 34
                34 [label=F]
                34 -> 35
                35 [label=num]
                v35 [label=6 color=blue shape=box]
                35 -> v35 [arrowhead=none color=blue style=dashed]
                11 [label="("]
                v11 [label="(" color=blue shape=box]
                11 -> v11 [arrowhead=none color=blue style=dashed]
                9 [label="*"]
                v9 [label="*" color=blue shape=box]
                9 -> v9 [arrowhead=none color=blue style=dashed]
                8 [label=T]
                8 -> 36
                36 [label=F]
                36 -> 37
                37 [label=num]
                v37 [label=3 color=blue shape=box]
                37 -> v37 [arrowhead=none color=blue style=dashed]
            }
            """,
            dot_source,
        )

    def test_regex(self):
        config = ptree.load_config('configs/test-parser-test-regex.yaml')
        grammar = ptree.Grammar(config)
        grammar.init()
        lexer = ptree.Lexer(config, symbol_pool=grammar.symbol_pool)
        parser = ptree.Parser(grammar)
        tokens = lexer.tokenize('(a|b)*abb|ef')
        parse_tree = parser.parse(tokens)
        dot_source = ptree.render(
            parse_tree,
            directory='out',
            name='test-parser-test-regex-parse-tree',
            output_format='svg',
        )
        self._assertDotEqual(
            """
            digraph {
                graph [rankdir=TB]
                0 [label=_S]
                0 -> 1
                1 [label=E]
                1 -> 2
                1 -> 3
                1 -> 4
                4 [label=T]
                4 -> 5
                4 -> 6
                6 [label=F]
                6 -> 7
                7 [label=P]
                7 -> 8
                8 [label=char]
                v8 [label=f color=blue shape=box]
                8 -> v8 [arrowhead=none color=blue style=dashed]
                5 [label=T]
                5 -> 9
                9 [label=F]
                9 -> 10
                10 [label=P]
                10 -> 11
                11 [label=char]
                v11 [label=e color=blue shape=box]
                11 -> v11 [arrowhead=none color=blue style=dashed]
                3 [label="|"]
                v3 [label="|" color=blue shape=box]
                3 -> v3 [arrowhead=none color=blue style=dashed]
                2 [label=E]
                2 -> 12
                12 [label=T]
                12 -> 13
                12 -> 14
                14 [label=F]
                14 -> 15
                15 [label=P]
                15 -> 16
                16 [label=char]
                v16 [label=b color=blue shape=box]
                16 -> v16 [arrowhead=none color=blue style=dashed]
                13 [label=T]
                13 -> 17
                13 -> 18
                18 [label=F]
                18 -> 19
                19 [label=P]
                19 -> 20
                20 [label=char]
                v20 [label=b color=blue shape=box]
                20 -> v20 [arrowhead=none color=blue style=dashed]
                17 [label=T]
                17 -> 21
                17 -> 22
                22 [label=F]
                22 -> 23
                23 [label=P]
                23 -> 24
                24 [label=char]
                v24 [label=a color=blue shape=box]
                24 -> v24 [arrowhead=none color=blue style=dashed]
                21 [label=T]
                21 -> 25
                25 [label=F]
                25 -> 26
                25 -> 27
                27 [label="*"]
                v27 [label="*" color=blue shape=box]
                27 -> v27 [arrowhead=none color=blue style=dashed]
                26 [label=F]
                26 -> 28
                26 -> 29
                26 -> 30
                30 [label=")"]
                v30 [label=")" color=blue shape=box]
                30 -> v30 [arrowhead=none color=blue style=dashed]
                29 [label=E]
                29 -> 31
                29 -> 32
                29 -> 33
                33 [label=T]
                33 -> 34
                34 [label=F]
                34 -> 35
                35 [label=P]
                35 -> 36
                36 [label=char]
                v36 [label=b color=blue shape=box]
                36 -> v36 [arrowhead=none color=blue style=dashed]
                32 [label="|"]
                v32 [label="|" color=blue shape=box]
                32 -> v32 [arrowhead=none color=blue style=dashed]
                31 [label=E]
                31 -> 37
                37 [label=T]
                37 -> 38
                38 [label=F]
                38 -> 39
                39 [label=P]
                39 -> 40
                40 [label=char]
                v40 [label=a color=blue shape=box]
                40 -> v40 [arrowhead=none color=blue style=dashed]
                28 [label="("]
                v28 [label="(" color=blue shape=box]
                28 -> v28 [arrowhead=none color=blue style=dashed]
            }
            """,
            dot_source
        )
