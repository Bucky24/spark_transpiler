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
                        Tree("variable", [Token('VARIABLE_NAME', 'foo')]),
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
                        Tree("variable", [Token('VARIABLE_NAME', 'foo')]),
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
                        Tree("variable", [Token('VARIABLE_NAME', 'bar')]),
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
                        Tree("variable", [Token('VARIABLE_NAME', 'foo')]),
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
                        Tree("variable", [Token('VARIABLE_NAME', 'foo')]),
                        Tree('statement', [
                            Token('NUMBER', '15.66'),
                        ]),
                    ]),
                ]),
            ]),
        ]))

        result = parse_statement("foo++")
        self.assertEqual(result, Tree('start', [
            Tree('statements', [
                Tree('statement', [
                    Tree('variable_increment', [
                        Tree("variable", [Token('VARIABLE_NAME', 'foo')]),
                    ]),
                ]),
            ]),
        ]))

        result = parse_statement("foo   ++")
        self.assertEqual(result, Tree('start', [
            Tree('statements', [
                Tree('statement', [
                    Tree('variable_increment', [
                        Tree("variable", [Token('VARIABLE_NAME', 'foo')]),
                    ]),
                ]),
            ]),
        ]))

        result = parse_statement("foo = bar as baz")
        self.assertEqual(result, Tree('start', [
            Tree('statements', [
                Tree('statement', [
                    Tree('variable_assignment', [
                        Tree("variable", [Token('VARIABLE_NAME', 'foo')]),
                        Tree('statement', [
                            Tree('variable_coercion', [
                                Tree("variable", [Token('VARIABLE_NAME', 'bar')]),
                                Token('TYPE', 'baz'),
                            ]),
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
                                Tree("variable", [Token('VARIABLE_NAME', 'foo')]),
                            ]),
                            Token('EQUALITY', '=='),
                            Tree('statement', [
                                Tree("variable", [Token('VARIABLE_NAME', 'bar')]),
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
                            Tree("variable", [Token('VARIABLE_NAME', 'foo')]),
                            Tree("variable", [Token('VARIABLE_NAME', 'bar')]),
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
                            Tree("variable", [Token('VARIABLE_NAME', 'foo')]),
                            Tree("variable", [Token('VARIABLE_NAME', 'bar')]),
                            Tree("variable", [Token('VARIABLE_NAME', 'baz')]),
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
                            Tree('statement_no_space', [
                                Tree("variable", [Token('VARIABLE_NAME', 'foo')]),  
                            ]),
                            Tree('statement_no_space', [
                                Tree("variable", [Token('VARIABLE_NAME', 'bar')]),
                            ]),
                            Tree('statement_no_space', [
                                Tree("variable", [Token('VARIABLE_NAME', 'baz')]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]))
        result2 = parse_statement("for    foo  ;   bar  ;  baz")
        self.assertEqual(result, result2)

    def test_while(self):
        result = parse_statement("while foo > bar")
        self.assertEqual(result, Tree('start', [
            Tree('statements', [
                Tree('statement', [
                    Tree('while', [
                        Tree('condition', [
                            Tree('statement', [
                                Tree("variable", [Token('VARIABLE_NAME', 'foo')]),
                            ]),
                            Token('EQUALITY', '>'),
                            Tree('statement', [
                                Tree("variable", [Token('VARIABLE_NAME', 'bar')]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]))

    def test_class(self):
        result = parse_statement("class Foo")
        self.assertEqual(result, Tree('start', [
            Tree('statements', [
                Tree('statement', [
                    Tree('class', [
                        Tree("variable", [Token('VARIABLE_NAME', 'Foo')]),
                    ]),
                ]),
            ]),
        ]))

        result = parse_statement("class Foo extends Bar")
        self.assertEqual(result, Tree('start', [
            Tree('statements', [
                Tree('statement', [
                    Tree('class', [
                        Tree("variable", [Token('VARIABLE_NAME', 'Foo')]),
                        Tree("variable", [Token("VARIABLE_NAME", "Bar")]),
                    ]),
                ]),
            ]),
        ]))
        result2 = parse_statement("class     Foo   extends    Bar")
        self.assertEqual(result, result2)

        result = parse_statement("bar.baz.foo = bin")
        print(result)
        self.assertEqual(result, Tree('start', [
            Tree('statements', [
                Tree('statement', [
                    Tree('variable_assignment', [
                        Tree("variable", [
                            Tree("instance_variable_chain", [
                                Token("VARIABLE_NAME", "bar"),
                                Token("VARIABLE_NAME", "baz"),
                                Token("VARIABLE_NAME", "foo"),
                            ]),
                        ]),
                        Tree("statement", [
                            Tree("variable", [Token("VARIABLE_NAME", "bin")]),
                        ]),
                    ]),
                ]),
            ]),
        ]))

    def test_function(self):
        result = parse_statement("function(a, b, c)")
        self.assertEqual(result, Tree("start", [
            Tree("statements", [
                Tree("statement", [
                    Tree("function_definition", [
                        Tree("first_param", [
                            Tree("variable", [Token("VARIABLE_NAME", "a")]),
                        ]),
                        Tree("param", [
                            Tree("variable", [Token("VARIABLE_NAME", "b")]),
                        ]),
                        Tree("param", [
                            Tree("variable", [Token("VARIABLE_NAME", "c")]),
                        ]),
                    ]),
                ]),
            ]),
        ]))
        result2 = parse_statement("function    (  a    ,    b   ,     c)")
        self.assertEqual(result, result2)

        result = parse_statement("function()")
        self.assertEqual(result, Tree("start", [
            Tree("statements", [
                Tree("statement", [
                    Tree("function_definition", []),
                ]),
            ]),
        ]))

        result = parse_statement("function foo()")
        self.assertEqual(result, Tree("start", [
            Tree("statements", [
                Tree("statement", [
                    Tree("function_definition", [
                        Tree('function_name', [
                            Tree("variable", [Token("VARIABLE_NAME", "foo")]),
                        ]),
                    ]),
                ]),
            ]),
        ]))
        result2 = parse_statement("function  foo  ( )")
        self.assertEqual(result, result2)

        result = parse_statement("function foo(a, b, c)")
        self.assertEqual(result, Tree("start", [
            Tree("statements", [
                Tree("statement", [
                    Tree("function_definition", [
                        Tree('function_name', [
                            Tree("variable", [Token("VARIABLE_NAME", "foo")]),
                        ]),
                        Tree("first_param", [
                            Tree("variable", [Token("VARIABLE_NAME", "a")]),
                        ]),
                        Tree("param", [
                            Tree("variable", [Token("VARIABLE_NAME", "b")]),
                        ]),
                        Tree("param", [
                            Tree("variable", [Token("VARIABLE_NAME", "c")]),
                        ]),
                    ]),
                ]),
            ]),
        ]))
        result2 = parse_statement("function  foo  (  a  ,  b  ,  c )")
        self.assertEqual(result, result2)

        result = parse_statement("foo(\n  a\n  b\n)")
        self.assertEqual(result, Tree("start", [
            Tree("statements", [
                Tree("statement", [
                    Tree("call_function", [
                        Tree("variable", [Token("VARIABLE_NAME", "foo")]),
                    ]),
                ]),
                Token("NEWLINE", "\n"),
                Tree("statement", [
                    Tree("spaces", [
                        Token("SPACE", " "),
                    ]),
                    Tree("spaces", [
                        Token("SPACE", " "),
                    ]),
                    Tree("variable", [Token("VARIABLE_NAME", "a")]),
                ]),
                Token("NEWLINE", "\n"),
                Tree("statement", [
                    Tree("spaces", [
                        Token("SPACE", " "),
                    ]),
                    Tree("spaces", [
                        Token("SPACE", " "),
                    ]),
                    Tree("variable", [Token("VARIABLE_NAME", "b")]),
                ]),
                Token("NEWLINE", "\n"),
                Tree("statement", [
                    Tree("end_call_function", []),
                ]),
            ]),
        ]))

    def test_nesting(self):
        result = parse_statement("foo = bar\n      foo = bar")
        self.assertEqual(result, Tree("start", [
            Tree("statements", [
                Tree("statement", [
                    Tree("variable_assignment", [
                        Tree("variable", [Token("VARIABLE_NAME", "foo")]),
                        Tree("statement", [
                            Tree("variable", [Token("VARIABLE_NAME", "bar")]),
                        ]),
                    ]),
                ]),
                Token("NEWLINE", "\n"),
                Tree("statement", [
                    Tree("spaces", [
                        Token("SPACE", " "),
                    ]),
                    Tree("spaces", [
                        Token("SPACE", " "),
                    ]),
                    Tree("spaces", [
                        Token("SPACE", " "),
                    ]),
                    Tree("spaces", [
                        Token("SPACE", " "),
                    ]),
                    Tree("spaces", [
                        Token("SPACE", " "),
                    ]),
                    Tree("spaces", [
                        Token("SPACE", " "),
                    ]),
                    Tree("variable_assignment", [
                        Tree("variable", [Token("VARIABLE_NAME", "foo")]),
                        Tree("statement", [
                            Tree("variable", [Token("VARIABLE_NAME", "bar")]),
                        ]),
                    ]),
                ]),
            ]),
        ]))

if __name__ == "__main__":
    unittest.main()