import unittest
from lark import tree
from lark import lexer

from grammar import parse_statement

"""
 bar = 'baz'
    if foo == \"bar\"
        fler = 14
    flar = 54423.542345
    for foo as bar : baz
        for i=0;i<5;i++
            foo = bar as string
"""

Tree = tree.Tree
Token = lexer.Token

class TestGrammar(unittest.TestCase):
    def test_variables(self):
        result = parse_statement("foo = \"bar\"")
        self.assertEqual(result, Tree('start', [
            Tree('statements', [
                Tree('statement', [
                    Tree('variable_assignment', [
                        Token('VARIABLE_NAME', 'foo'),
                        Tree('statement', [
                            Tree('string', [
                                Token('STRING_CONTENTS_DOUBLE', 'bar'),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]))

        result = parse_statement("foo = \"bar\"\nbar = 'baz'")
        self.assertEqual(result, Tree('start', [
            Tree('statements', [
                Tree('statement', [
                    Tree('variable_assignment', [
                        Token('VARIABLE_NAME', 'foo'),
                        Tree('statement', [
                            Tree('string', [
                                Token('STRING_CONTENTS_DOUBLE', 'bar'),
                            ]),
                        ]),
                    ]),
                ]),
                Token('NEWLINE', '\n'),
                Tree('statement', [
                    Tree('variable_assignment', [
                        Token('VARIABLE_NAME', 'bar'),
                        Tree('statement', [
                            Tree('string', [
                                Token('STRING_CONTENTS_SINGLE', 'baz'),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]))

        result = parse_statement("foo= 15")
        self.assertEqual(result, Tree('start', [
            Tree('statements', [
                Tree('statement', [
                    Tree('variable_assignment', [
                        Token('VARIABLE_NAME', 'foo'),
                        Tree('statement', [
                            Token('NUMBER', '15'),
                        ]),
                    ]),
                ]),
            ]),
        ]))

        result = parse_statement("foo =15.66")
        self.assertEqual(result, Tree('start', [
            Tree('statements', [
                Tree('statement', [
                    Tree('variable_assignment', [
                        Token('VARIABLE_NAME', 'foo'),
                        Tree('statement', [
                            Token('NUMBER', '15.66'),
                        ]),
                    ]),
                ]),
            ]),
        ]))

    def test_if(self):
        result = parse_statement("if foo == bar")
        self.assertEqual(result, Tree('start', [
            Tree('statements', [
                Tree('statement', [
                    Tree('if', [
                        Tree('condition', [
                            Tree('statement', [
                                Token('VARIABLE_NAME', 'foo'),
                            ]),
                            Token('EQUALITY', '=='),
                            Tree('statement', [
                                Token('VARIABLE_NAME', 'bar'),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]))
        result = parse_statement("if foo > bar")
        self.assertEqual(
            result.children[0].children[0].children[0].children[0].children[1],
            Token('EQUALITY', '>'),
        )
        result = parse_statement("if foo < bar")
        self.assertEqual(
            result.children[0].children[0].children[0].children[0].children[1],
            Token('EQUALITY', '<'),
        )
        result = parse_statement("if foo <= bar")
        self.assertEqual(
            result.children[0].children[0].children[0].children[0].children[1],
            Token('EQUALITY', '<='),
        )
        result = parse_statement("if foo >= bar")
        self.assertEqual(
            result.children[0].children[0].children[0].children[0].children[1],
            Token('EQUALITY', '>='),
        )
        result = parse_statement("if foo != bar")
        self.assertEqual(
            result.children[0].children[0].children[0].children[0].children[1],
            Token('EQUALITY', '!='),
        )

    def test_for(self):
        result = parse_statement("for foo as bar")
        self.assertEqual(result, Tree('start', [
            Tree('statements', [
                Tree('statement', [
                    Tree('for', [
                        Tree('for_array', [
                            Token('VARIABLE_NAME', 'foo'),
                            Token('VARIABLE_NAME', 'bar'),
                        ]),
                    ]),
                ]),
            ]),
        ]))
        result2 = parse_statement("for   foo   as   bar")
        self.assertEqual(result, result2)

        result = parse_statement("for foo as bar : baz")
        self.assertEqual(result, Tree('start', [
            Tree('statements', [
                Tree('statement', [
                    Tree('for', [
                        Tree('for_object', [
                            Token('VARIABLE_NAME', 'foo'),
                            Token('VARIABLE_NAME', 'bar'),
                            Token('VARIABLE_NAME', 'baz'),
                        ]),
                    ]),
                ]),
            ]),
        ]))
        result2 = parse_statement("for foo as bar: baz")
        self.assertEqual(result, result2)
        result2 = parse_statement("for foo as bar :baz")
        self.assertEqual(result, result2)
        result2 = parse_statement("for foo as bar:baz")
        self.assertEqual(result, result2)
        result2 = parse_statement("for   foo   as   bar   :  baz")
        self.assertEqual(result, result2)

        result = parse_statement("for foo;bar;baz")
        self.assertEqual(result, Tree('start', [
            Tree('statements', [
                Tree('statement', [
                    Tree('for', [
                        Tree('for_statement', [
                            Tree('statement', [
                                Token('VARIABLE_NAME', 'foo'),  
                            ]),
                            Tree('statement', [
                                Token('VARIABLE_NAME', 'bar'),
                            ]),
                            Tree('statement', [
                                Token('VARIABLE_NAME', 'baz'),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]))
        result2 = parse_statement("for    foo  ;   bar  ;  baz")
        self.assertEqual(result, result2)

if __name__ == "__main__":
    unittest.main()