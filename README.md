# LR(1) Parse Tree Generator

![Python-3.10](https://img.shields.io/badge/Python-3.10-blue)
![version-0.1.4](https://img.shields.io/badge/version-0.1.4-blue)
[![license-MIT](https://img.shields.io/badge/license-MIT-green)](https://github.com/AlumiK/parse-tree/blob/main/LICENSE)

## Demo

Modify the config file if necessary and then execute:

```
python demo.py --config=<config> --text=<text>
```

The image of the output parse tree will be saved in `out/parse-tree.svg`. (This behavior can be changed in `demo.py`.)

## Examples

### Lexical Analysis

#### NFA to DFA

Take the regular expression `(a|b)*abb` for example.

1. Create an NFA from the regular expression:
   
    ```python
    from ptree.lexer.regex import Regex, RegexEngine

    regex = Regex(name='(a|b)*abb', pattern='(a|b)*abb')
    engine = RegexEngine()
    nfa = engine.parse(regex)
    nfa.render(directory='out', name='nfa', output_format='svg')
    ```
    
    ![NFA](https://raw.githubusercontent.com/AlumiK/images/main/parse-tree/test-nfa-to-dfa-nfa.svg)
    
2. Convert the NFA to a DFA:

    ```python
    dfa = nfa.to_dfa()
    dfa.render(directory='out', name='dfa', output_format='svg')
    ```

    ![DFA](https://raw.githubusercontent.com/AlumiK/images/main/parse-tree/test-nfa-to-dfa-dfa.svg)

#### Merge multiple NFAs

Take the regular expressions `a*b+`, `a`, `abb` for example.

1. Create three NFAs from the regular expressions.

    ```python
    from ptree.lexer.regex import Regex, RegexEngine

    regexes = [
        Regex(name='a*b+', pattern='a*b+'),
        Regex(name='a', pattern='a'),
        Regex(name='abb', pattern='abb')
    ]
    engine = RegexEngine()
    nfas = [engine.parse(regex) for regex in regexes]
    for i, nfa in enumerate(nfas):
        nfa.render(directory='out', name=f'nfa-{i}', output_format='svg')
    ```

    ![NFA-1](https://raw.githubusercontent.com/AlumiK/images/main/parse-tree/test-merge-fsm-nfa0.svg)

    ![NFA-2](https://raw.githubusercontent.com/AlumiK/images/main/parse-tree/test-merge-fsm-nfa1.svg)

    ![NFA-3](https://raw.githubusercontent.com/AlumiK/images/main/parse-tree/test-merge-fsm-nfa2.svg)

2. Merge the NFAs.

    ```python
    from ptree.lexer.nfa import NFA

    nfa = NFA.union(nfas)
    nfa.render(directory='out', name='nfa', output_format='svg')
    ```
   
    ![NFA](https://raw.githubusercontent.com/AlumiK/images/main/parse-tree/test-merge-fsm-nfa.svg)

3. Convert the NFA to DFA.

    ```python
    dfa = nfa.to_dfa()
    dfa.render(directory='out', name='dfa', output_format='svg')
    ```

    ![DFA](https://raw.githubusercontent.com/AlumiK/images/main/parse-tree/test-merge-fsm-dfa.svg)

#### Tokenize a string

The config file used in this example is:

```yaml
nonterminal_symbols:
terminal_symbols:
  COMMENT: '(//[^\n]*)|(/\*([^\*]|(\*)*[^\*/])*(\*)*\*/)'
  KEYWORD: 'auto|short|int|long|float|double|char|struct|union|enum|typedef|const|unsigned|signed|extern|register|static|volatile|void|if|else|switch|case|for|do|while|goto|continue|break|default|sizeof|return|using|namespace'
  IDENTIFIER: '[A-Za-z_][A-Za-z0-9_]*'
  INTEGER: '[0-9]+'
  FLOAT: '[0-9]+\.[0-9]+'
  COMPARISON: '==|>|<|>=|<=|!='
  LSTREAM: '<<'
  RSTREAM: '>>'
  LP: '\('
  RP: '\)'
  LB: '{'
  RB: '}'
  COMMA: ','
  SEMICOLON: ';'
  LSB: '\['
  RSB: '\]'
  ASSIGN_OP: '='
  ADD_OP: '\+'
  SUB_OP: '\-'
  MULT_OP: '\*'
  DIV_OP: '/'
  MOD_OP: '%'
  POWER_OP: '\^'
  AND_OP: '&&'
  OR_OP: '\|\|'
  NOT_OP: '!'
  SPACE: '[ \t\n\r]+'
ignored_symbols:
  ? SPACE
  ? COMMENT
start_symbol:
production_rules:
```

The input string is:

```cpp
int main() {int a = a + 1; cout << a << endl; return 0;}
```

1. Create a lexer from the config file.

    ```python
    import ptree

    config = ptree.load_config('config.yaml')
    grammar = ptree.Grammar(config)
    lexer = ptree.Lexer(config, symbol_pool=grammar.symbol_pool)
    ```
   
2. Tokenize the input string.

    ```python
    tokens = lexer.tokenize('''int main() {int a = a + 1; cout << a << endl; return 0;}''')
    ptree.pretty_print_tokens(tokens)
    ```
   
    ```
    +----+------------+--------+
    |    | SYMBOL     | VALUE  |
    +====+============+========+
    | 1  | KEYWORD    | int    |
    +----+------------+--------+
    | 2  | IDENTIFIER | main   |
    +----+------------+--------+
    | 3  | LP         | (      |
    +----+------------+--------+
    | 4  | RP         | )      |
    +----+------------+--------+
    | 5  | LB         | {      |
    +----+------------+--------+
    | 6  | KEYWORD    | int    |
    +----+------------+--------+
    | 7  | IDENTIFIER | a      |
    +----+------------+--------+
    | 8  | ASSIGN_OP  | =      |
    +----+------------+--------+
    | 9  | IDENTIFIER | a      |
    +----+------------+--------+
    | 10 | ADD_OP     | +      |
    +----+------------+--------+
    | 11 | INTEGER    | 1      |
    +----+------------+--------+
    | 12 | SEMICOLON  | ;      |
    +----+------------+--------+
    | 13 | IDENTIFIER | cout   |
    +----+------------+--------+
    | 14 | LSTREAM    | <<     |
    +----+------------+--------+
    | 15 | IDENTIFIER | a      |
    +----+------------+--------+
    | 16 | LSTREAM    | <<     |
    +----+------------+--------+
    | 17 | IDENTIFIER | endl   |
    +----+------------+--------+
    | 18 | SEMICOLON  | ;      |
    +----+------------+--------+
    | 19 | KEYWORD    | return |
    +----+------------+--------+
    | 20 | INTEGER    | 0      |
    +----+------------+--------+
    | 21 | SEMICOLON  | ;      |
    +----+------------+--------+
    | 22 | RB         | }      |
    +----+------------+--------+
    ```

### Creating Parse Tree

1. Get the predefined grammar.

    ```
    1. S'->S
    2. S->CβBA
    3. A->Aαβ
    4. A->αβ
    5. B->C
    6. B->Dβ
    7. C->α
    8. D->α
    ```

2. Write a config file (in YAML format).

    ```yaml
    nonterminal_symbols:
        # ? name
        ? A
        ? B
        ? C
        ? D
        ? S
    terminal_symbols:
        # name: regex
        α: a
        β: b
    ignored_symbols:
    start_symbol: S
    production_rules:
        # - left part -> right part
        - S -> C β B A
        - A -> A α β
        - A -> α β
        - B -> C
        - B -> D β
        - C -> α
        - D -> α
    ```

3. Generate the parse table.

    ```python
    import ptree

    config = ptree.load_config('config.yaml')
    grammar = ptree.Grammar(config)
    grammar.init()
    parser = ptree.Parser(grammar)
    print(grammar.parse_table)
    ```
   
    ```
    +----+-----------------+-------------------+-----------------------------------------------------------------------------------------+
    |    | ACTION          | GOTO              | STATE                                                                                   |
    +----+-----+-----+-----+---+---+---+---+---+-----------------------------------------------------------------------------------------+
    |    | α   | β   | $   | A | B | C | D | S |                                                                                         |
    +----+-----+-----+-----+---+---+---+---+---+-----------------------------------------------------------------------------------------+
    | 0  | s1  |     |     |   |   | 3 |   | 2 | {C ->  . α, β; _S ->  . S, $; S ->  . C β B A, $}                                       |
    +----+-----+-----+-----+---+---+---+---+---+-----------------------------------------------------------------------------------------+
    | 1  |     | r6  |     |   |   |   |   |   | {C -> α . , β}                                                                          |
    +----+-----+-----+-----+---+---+---+---+---+-----------------------------------------------------------------------------------------+
    | 2  |     |     | acc |   |   |   |   |   | {_S -> S . , $}                                                                         |
    +----+-----+-----+-----+---+---+---+---+---+-----------------------------------------------------------------------------------------+
    | 3  |     | s4  |     |   |   |   |   |   | {S -> C . β B A, $}                                                                     |
    +----+-----+-----+-----+---+---+---+---+---+-----------------------------------------------------------------------------------------+
    | 4  | s5  |     |     |   | 6 | 8 | 7 |   | {C ->  . α, α; S -> C β . B A, $; D ->  . α, β; B ->  . D β, α; B ->  . C, α}           |
    +----+-----+-----+-----+---+---+---+---+---+-----------------------------------------------------------------------------------------+
    | 5  | r6  | r7  |     |   |   |   |   |   | {C -> α . , α; D -> α . , β}                                                            |
    +----+-----+-----+-----+---+---+---+---+---+-----------------------------------------------------------------------------------------+
    | 6  | s10 |     |     | 9 |   |   |   |   | {A ->  . A α β, $; A ->  . A α β, α; A ->  . α β, $; S -> C β B . A, $; A ->  . α β, α} |
    +----+-----+-----+-----+---+---+---+---+---+-----------------------------------------------------------------------------------------+
    | 7  |     | s11 |     |   |   |   |   |   | {B -> D . β, α}                                                                         |
    +----+-----+-----+-----+---+---+---+---+---+-----------------------------------------------------------------------------------------+
    | 8  | r4  |     |     |   |   |   |   |   | {B -> C . , α}                                                                          |
    +----+-----+-----+-----+---+---+---+---+---+-----------------------------------------------------------------------------------------+
    | 9  | s12 |     | r1  |   |   |   |   |   | {A -> A . α β, $; A -> A . α β, α; S -> C β B A . , $}                                  |
    +----+-----+-----+-----+---+---+---+---+---+-----------------------------------------------------------------------------------------+
    | 10 |     | s13 |     |   |   |   |   |   | {A -> α . β, $; A -> α . β, α}                                                          |
    +----+-----+-----+-----+---+---+---+---+---+-----------------------------------------------------------------------------------------+
    | 11 | r5  |     |     |   |   |   |   |   | {B -> D β . , α}                                                                        |
    +----+-----+-----+-----+---+---+---+---+---+-----------------------------------------------------------------------------------------+
    | 12 |     | s14 |     |   |   |   |   |   | {A -> A α . β, $; A -> A α . β, α}                                                      |
    +----+-----+-----+-----+---+---+---+---+---+-----------------------------------------------------------------------------------------+
    | 13 | r3  |     | r3  |   |   |   |   |   | {A -> α β . , $; A -> α β . , α}                                                        |
    +----+-----+-----+-----+---+---+---+---+---+-----------------------------------------------------------------------------------------+
    | 14 | r2  |     | r2  |   |   |   |   |   | {A -> A α β . , $; A -> A α β . , α}                                                    |
    +----+-----+-----+-----+---+---+---+---+---+-----------------------------------------------------------------------------------------+
    ```

4. Tokenize the input string.

    The input string is `abababab`.

    ```python
    lexer = ptree.Lexer(config, symbol_pool=grammar.symbol_pool)
    tokens = lexer.tokenize('abababab')
    ptree.pretty_print_tokens(tokens)
    ```
   
    ![DFA](https://raw.githubusercontent.com/AlumiK/images/main/parse-tree/lexer-dfa.svg)
   
    ```
    +---+--------+-------+
    |   | SYMBOL | VALUE |
    +===+========+=======+
    | 1 | α      | a     |
    +---+--------+-------+
    | 2 | β      | b     |
    +---+--------+-------+
    | 3 | α      | a     |
    +---+--------+-------+
    | 4 | β      | b     |
    +---+--------+-------+
    | 5 | α      | a     |
    +---+--------+-------+
    | 6 | β      | b     |
    +---+--------+-------+
    | 7 | α      | a     |
    +---+--------+-------+
    | 8 | β      | b     |
    +---+--------+-------+
    ```

5. Generate the parse tree.

    ```python
    parse_tree = parser.parse(tokens)
    parse_tree.render(directory='out', name='parse-tree', output_format='svg')
    ```

    ![Parse Tree](https://raw.githubusercontent.com/AlumiK/images/main/parse-tree/parse-tree.svg)
