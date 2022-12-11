import unittest
#from lark import tree
#from lark import lexer

from grammar import parse_statement, Tree, Token
from utils import print_tree

if 'unittest.util' in __import__('sys').modules:
    # Show full diff in self.assertEqual.
    __import__('sys').modules['unittest.util']._MAX_LENGTH = 999999999

"""
 bar = 'baz'
    if foo == \"bar\"
        fler = 14
    flar = 54423.542345
    for foo as bar : baz
        for i=0;i<5;i++
            foo = bar as string
"""

#Tree = lark.Tree
#Token = lark.Token

def _get_start(contents):
    return Tree("start", [
        Tree("statements", contents),
    ])

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

        result = parse_statement("foo = \"bar\"\nbar = 'baz'\n")
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
                Token("NEWLINE", "\n"),
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
                    Tree('if_stat', [
                        Tree('condition', [
                            Tree('statement', [
                                Tree("variable", [Token('VARIABLE_NAME', 'foo')]),
                            ]),
                            Token('EQUALITY', '=='),
                            Tree('statement', [
                                Tree("variable", [Token('VARIABLE_NAME', 'bar')]),
                            ]),
                        ]),
                        Tree("nested", []),
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

        result = parse_statement("if foo == \"bar\"\n\tbar = foo\nfoo = bar")
        self.assertEqual(result, Tree('start', [
            Tree("statements", [
                Tree("statement", [
                    Tree("if_stat", [
                        Tree("condition", [
                            Tree("statement", [
                                Tree("variable", [Token("VARIABLE_NAME", "foo")]),
                            ]),
                            Token("EQUALITY", "=="),
                            Tree("statement", [
                                Tree("string", [Token("STRING_CONTENTS_DOUBLE", "bar")]),
                            ]),
                        ]),
                        Tree("nested", [
                            Tree("statement", [
                                Tree("spaces", [Token("TAB", "\t")]),
                                Tree("variable_assignment", [
                                    Tree("variable", [Token("VARIABLE_NAME", "bar")]),
                                    Tree("statement", [
                                        Tree("variable", [Token("VARIABLE_NAME", "foo")]),
                                    ]),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
                Tree("statement", [
                    Tree("variable_assignment", [
                        Tree("variable", [Token("VARIABLE_NAME", "foo")]),
                        Tree("statement", [
                            Tree("variable", [Token("VARIABLE_NAME", "bar")]),
                        ]),
                    ]),
                ]),
            ]),
        ]))

        # fixing a complex little bug where the system was treating "if" as a variable name
        # only if there were statements before it
        result = parse_statement("""foo = \"bar\"
if foo == \"bar\"
    bar = foo
""")
        self.assertEqual(result, Tree('start', [
            Tree('statements', [
                Tree("statement", [
                    Tree("variable_assignment", [
                        Tree("variable", [
                            Token("VARIABLE_NAME", "foo"),
                        ]),
                        Tree("statement", [
                            Tree("string", [
                                Token("STRING_CONTENTS_DOUBLE", "bar"),
                            ]),
                        ]),
                    ]),
                ]),
                Token("NEWLINE", "\n"),
                Tree('statement', [
                    Tree('if_stat', [
                        Tree('condition', [
                            Tree('statement', [
                                Tree("variable", [Token('VARIABLE_NAME', 'foo')]),
                            ]),
                            Token('EQUALITY', '=='),
                            Tree('statement', [
                                Tree("string", [Token('STRING_CONTENTS_DOUBLE', 'bar')]),
                            ]),
                        ]),
                        Tree("nested", [
                            Tree("statement", [
                                Tree("spaces", [Token("SPACE", " ")]),
                                Tree("spaces", [Token("SPACE", " ")]),
                                Tree("spaces", [Token("SPACE", " ")]),
                                Tree("spaces", [Token("SPACE", " ")]),
                                Tree("variable_assignment", [
                                    Tree("variable", [
                                        Token("VARIABLE_NAME", "bar"),
                                    ]),
                                    Tree("statement", [
                                        Tree("variable", [
                                            Token("VARIABLE_NAME", "foo"),
                                        ]),
                                    ]),
                                ]),
                            ]),
                        ])
                    ]),
                ]),
            ]),
        ]))

    def test_for(self):
        result = parse_statement("for foo as bar")
        self.assertEqual(result, Tree('start', [
            Tree('statements', [
                Tree('statement', [
                    Tree('for_stat', [
                        Tree('for_array', [
                            Tree("variable", [Token('VARIABLE_NAME', 'foo')]),
                            Tree("variable", [Token('VARIABLE_NAME', 'bar')]),
                        ]),
                        Tree("nested", []),
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
                    Tree('for_stat', [
                        Tree('for_object', [
                            Tree("variable", [Token('VARIABLE_NAME', 'foo')]),
                            Tree("variable", [Token('VARIABLE_NAME', 'bar')]),
                            Tree("variable", [Token('VARIABLE_NAME', 'baz')]),
                        ]),
                        Tree("nested", []),
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
                    Tree('for_stat', [
                        Tree('for_statement', [
                            Tree('statement', [
                                Tree("variable", [Token('VARIABLE_NAME', 'foo')]),  
                            ]),
                            Tree('statement', [
                                Tree("variable", [Token('VARIABLE_NAME', 'bar')]),
                            ]),
                            Tree('statement', [
                                Tree("variable", [Token('VARIABLE_NAME', 'baz')]),
                            ]),
                        ]),
                        Tree("nested", []),
                    ]),
                ]),
            ]),
        ]))
        result2 = parse_statement("for    foo  ;   bar  ;  baz")
        self.assertEqual(result, result2)

        result = parse_statement("for foo=0;foo<5;foo++")
        self.assertEqual(result, Tree('start', [
            Tree('statements', [
                Tree('statement', [
                    Tree('for_stat', [
                        Tree('for_statement', [
                            Tree('statement', [
                                Tree("variable_assignment", [
                                    Tree("variable", [Token('VARIABLE_NAME', 'foo')]),
                                    Tree("statement", [Token("NUMBER", "0")]),
                                ])  
                            ]),
                            Tree('statement', [
                                Tree("condition", [
                                    Tree("statement", [
                                        Tree("variable", [Token('VARIABLE_NAME', 'foo')]),
                                    ]),
                                    Token("EQUALITY", "<"),
                                    Tree("statement", [Token("NUMBER", "5")]),
                                ]),
                            ]),
                            Tree('statement', [
                                Tree("variable_increment", [
                                    Tree("variable", [Token('VARIABLE_NAME', 'foo')]),
                                ]),
                            ]),
                        ]),
                        Tree("nested", []),
                    ]),
                ]),
            ]),
        ]))

    def test_while(self):
        result = parse_statement("while foo > bar")
        self.assertEqual(result, Tree('start', [
            Tree('statements', [
                Tree('statement', [
                    Tree('while_stat', [
                        Tree('condition', [
                            Tree('statement', [
                                Tree("variable", [Token('VARIABLE_NAME', 'foo')]),
                            ]),
                            Token('EQUALITY', '>'),
                            Tree('statement', [
                                Tree("variable", [Token('VARIABLE_NAME', 'bar')]),
                            ]),
                        ]),
                        Tree("nested", []),
                    ]),
                ]),
            ]),
        ]))

    def test_class(self):
        result = parse_statement("class Foo")
        self.assertEqual(result, Tree('start', [
            Tree('statements', [
                Tree('statement', [
                    Tree('class_stat', [
                        Tree("variable", [Token('VARIABLE_NAME', 'Foo')]),
                        Tree("nested", []),
                    ]),
                ]),
            ]),
        ]))

        result = parse_statement("class Foo extends Bar")
        self.assertEqual(result, Tree('start', [
            Tree('statements', [
                Tree('statement', [
                    Tree('class_stat', [
                        Tree("variable", [Token('VARIABLE_NAME', 'Foo')]),
                        Tree("variable", [Token("VARIABLE_NAME", "Bar")]),
                        Tree("nested", []),
                    ]),
                ]),
            ]),
        ]))
        result2 = parse_statement("class     Foo   extends    Bar")
        self.assertEqual(result, result2)

        result = parse_statement("bar.baz.foo = bin")
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
        
        result = parse_statement("bar.baz.foo()")
        self.assertEqual(result, Tree('start', [
            Tree('statements', [
                Tree('statement', [
                    Tree('call_function', [
                        Tree("function_name", [
                            Tree("statement", [
                                Tree("variable", [
                                    Tree("instance_variable_chain", [
                                        Token("VARIABLE_NAME", "bar"),
                                        Token("VARIABLE_NAME", "baz"),
                                        Token("VARIABLE_NAME", "foo"),
                                    ]),
                                ]),
                            ]),
                        ]),
                        Tree("function_params", []),
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
                        Tree("param", [
                            Tree("variable", [Token("VARIABLE_NAME", "a")]),
                        ]),
                        Tree("param", [
                            Tree("variable", [Token("VARIABLE_NAME", "b")]),
                        ]),
                        Tree("param", [
                            Tree("variable", [Token("VARIABLE_NAME", "c")]),
                        ]),
                        Tree("nested", []),
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
                    Tree("function_definition", [
                        Tree("nested", []),
                    ]),
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
                        Tree("nested", []),
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
                        Tree("param", [
                            Tree("variable", [Token("VARIABLE_NAME", "a")]),
                        ]),
                        Tree("param", [
                            Tree("variable", [Token("VARIABLE_NAME", "b")]),
                        ]),
                        Tree("param", [
                            Tree("variable", [Token("VARIABLE_NAME", "c")]),
                        ]),
                        Tree("nested", []),
                    ]),
                ]),
            ]),
        ]))
        result2 = parse_statement("function  foo  (  a  ,  b  ,  c )")
        self.assertEqual(result, result2)

        result = parse_statement("foo(\n  a\n  b\n)\n")
        self.assertEqual(result, Tree("start", [
            Tree("statements", [
                Tree("statement", [
                    Tree("call_function", [
                        Tree("function_name", [
                            Tree('statement', [
                                Tree("variable", [Token("VARIABLE_NAME", "foo")]),
                            ]),
                        ]),
                        Tree("function_params", [
                            Token("NEWLINE", "\n"),
                            Tree("statement", [
                                Tree("variable", [Token("VARIABLE_NAME", "a")]),
                            ]),
                            Token("NEWLINE", "\n"),
                            Tree("statement", [
                                Tree("variable", [Token("VARIABLE_NAME", "b")]),
                            ]),
                        ]),
                    ]),
                ]),
                Token("NEWLINE", "\n"),
            ]),
        ]))

    def test_nesting(self):
        result = parse_statement("foo = bar\n      foo = bar\n")
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
                Token("NEWLINE", "\n"),
            ]),
        ]))

    def test_pragma(self):
        result = parse_statement("#foobar")
        self.assertEqual(result, Tree("start", [
            Tree("statements", [
                Tree("statement", [
                    Tree("pragma", [
                        Token("PRAGMA_NAME", "foobar"),
                    ]),
                ]),
            ]),
        ]))

        result = parse_statement("#  FOOBAR")
        self.assertEqual(result, Tree("start", [
            Tree("statements", [
                Tree("statement", [
                    Tree("pragma", [
                        Token("PRAGMA_NAME", "FOOBAR"),
                    ]),
                ]),
            ]),
        ]))

        result = parse_statement("#  FOObar")
        self.assertEqual(result, Tree("start", [
            Tree("statements", [
                Tree("statement", [
                    Tree("pragma", [
                        Token("PRAGMA_NAME", "FOObar"),
                    ]),
                ]),
            ]),
        ]))
        
        result = parse_statement("#  FOO     bar")
        self.assertEqual(result, Tree("start", [
            Tree("statements", [
                Tree("statement", [
                    Tree("pragma", [
                        Token("PRAGMA_NAME", "FOO"),
                        Token("PRAGMA_VALUE", "bar"),
                    ]),
                ]),
            ]),
        ]))

        result = parse_statement("#foo bar,baz")
        self.assertEqual(result, Tree("start", [
            Tree("statements", [
                Tree("statement", [
                    Tree("pragma", [
                        Token("PRAGMA_NAME", "foo"),
                        Token("PRAGMA_VALUE", "bar"),
                        Token("PRAGMA_VALUE", "baz"),
                    ]),
                ]),
            ]),
        ]))
        
    def test_tabs_and_spaces(self):
        result = parse_statement("foo = bar\n    foo = bar\n\tfoo = bar\n")
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
                    Tree("spaces", [Token("SPACE", " ")]),
                    Tree("spaces", [Token("SPACE", " ")]),
                    Tree("spaces", [Token("SPACE", " ")]),
                    Tree("spaces", [Token("SPACE", " ")]),
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
                        Token("TAB", "\t"),
                    ]),
                    Tree("variable_assignment", [
                        Tree("variable", [Token("VARIABLE_NAME", "foo")]),
                        Tree("statement", [
                            Tree("variable", [Token("VARIABLE_NAME", "bar")]),
                        ]),
                    ]),
                ]),
                Token("NEWLINE", "\n"),
            ]),
        ]))
        
    def test_arrays(self):
        result = parse_statement("foo = [\n\t'bar'\n\t'baz'\n]\n")
        self.assertEqual(result, Tree("start", [
            Tree("statements", [
                Tree("statement", [
                    Tree("variable_assignment", [
                        Tree("variable", [Token("VARIABLE_NAME", "foo")]),
                        Tree("statement", [
                            Tree("array", [
                                Tree("statement", [
                                    Tree("spaces", [Token("TAB", "\t")]),
                                    Tree("string", [Token("STRING_CONTENTS_SINGLE", "bar")])
                                ]),
                                Tree("statement", [
                                Tree("spaces", [Token("TAB", "\t")]),
                                Tree("string", [Token("STRING_CONTENTS_SINGLE", "baz")])
                            ]),
                            ]),
                        ]),
                    ]),
                ]),
                Token("NEWLINE", "\n"),
            ]),
        ]))

        result = parse_statement("foo = []")
        self.assertEqual(result, _get_start([
            Tree("statement", [
                Tree("variable_assignment", [
                    Tree("variable", [Token("VARIABLE_NAME", "foo")]),
                    Tree("statement", [
                        Tree("array", []),
                    ]),
                ]),
            ]),
        ]))
        
    def test_maps(self):
        result = parse_statement("foo = {\n\tabcd: 'foo'\n}\n")
        self.assertEqual(result, Tree("start", [
            Tree("statements", [
                Tree("statement", [
                    Tree("variable_assignment", [
                        Tree("variable", [Token("VARIABLE_NAME", "foo")]),
                        Tree("statement", [
                            Tree("map", [
                                Tree("statement", [
                                    Tree("map_row", [
                                        Token("VARIABLE_NAME", "abcd"),
                                        Tree("statement", [
                                            Tree("string", [
                                                Token("STRING_CONTENTS_SINGLE", "foo"),
                                            ]),
                                        ]),
                                    ]),
                                ]),
                            ])
                        ])
                    ])
                ]),
                Token("NEWLINE", "\n"),
            ]),
        ]))
        
    def test_nested_map_array(self):
        result = parse_statement("foo = {\n\tkey: [\n\t\t{\n\t\t\tfoo: 'bar'\n\t\t}\n\t]\n}\n")
        self.assertEqual(result, Tree("start", [
            Tree("statements", [
                Tree("statement", [
                    Tree("variable_assignment", [
                        Tree("variable", [Token("VARIABLE_NAME", "foo")]),
                        Tree("statement", [
                            Tree("map", [
                                Tree("statement", [
                                    Tree("map_row", [
                                        Token("VARIABLE_NAME", "key"),
                                        Tree("statement", [
                                            Tree("array", [
                                                Tree("statement", [
                                                    Tree("spaces", [Token("TAB", "	")]),
                                                    Tree("spaces", [Token("TAB", "	")]),
                                                    Tree("map", [
                                                        Tree("statement", [
                                                            Tree("map_row", [
                                                                Token("VARIABLE_NAME", "foo"),
                                                                Tree("statement", [
                                                                    Tree("string", [
                                                                        Token("STRING_CONTENTS_SINGLE", "bar"),
                                                                    ]),
                                                                ]),
                                                            ]),
                                                        ]),
                                                    ]),
                                                ]),
                                            ]),
                                        ]),
                                    ]),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
                Token("NEWLINE", "\n"),
            ]),
        ]))
        
    def test_jsx(self):
        result = parse_statement("<div>\n</div>\n")
        self.assertEqual(result, Tree("start", [
            Tree("statements", [
                Tree("statement", [
                    Tree("jsx_tag_start", [
                        Token("TAG_NAME", "div"),
                        Tree("statement", [Tree("jsx_tag_end", [])]),
                        Tree("statement", [
                            Tree("jsx_end_tag", [
                                Token("TAG_NAME", "div"),
                            ])
                        ]),
                    ]),
                ]),
                Token("NEWLINE", "\n"),
            ]),
        ]))

        result = parse_statement("<div/>")
        self.assertEqual(result, Tree("start", [
            Tree("statements", [
                Tree("statement", [
                    Tree("jsx_tag_start", [
                        Token("TAG_NAME", "div"),
                        Tree("statement", [Tree("jsx_tag_end", [])]),
                        Token("TAG_SELF_CLOSE", "/"),
                    ]),
                ]),
            ]),
        ]))

        result = parse_statement("<div\n\tfoo=\"bar\"\n>\n</div>\n")
        self.assertEqual(result, Tree("start", [
            Tree("statements", [
                Tree("statement", [
                    Tree("jsx_tag_start", [
                        Token("TAG_NAME", "div"),
                        Tree("statement", [
                            Tree("jsx_attribute", [
                                Tree("variable", [
                                    Token("VARIABLE_NAME", "foo"),
                                ]),
                                Tree("statement", [
                                    Tree("string", [
                                        Token("STRING_CONTENTS_DOUBLE", "bar"),
                                    ]),
                                ]),
                            ]),
                        ]),
                        Tree("statement", [Tree("jsx_tag_end", [])]),
                        Tree("statement", [
                            Tree("jsx_end_tag", [
                                Token("TAG_NAME", "div"),
                            ])
                        ]),
                    ]),
                ]),
                Token("NEWLINE", "\n"),
            ]),
        ]))

        result = parse_statement("<div foo={bar} />\n")
        self.assertEqual(result, Tree("start", [
            Tree("statements", [
                Tree("statement", [
                    Tree("jsx_tag_start", [
                        Token("TAG_NAME", "div"),
                        Tree("statement", [
                            Tree("jsx_attribute", [
                                Tree("variable", [
                                    Token("VARIABLE_NAME", "foo"),
                                ]),
                                Tree("statement", [
                                    Tree("variable", [
                                        Token("VARIABLE_NAME", "bar"),
                                    ]),
                                ]),
                            ]),
                        ]),
                        Tree("statement", [Tree("jsx_tag_end", [])]),
                        Token("TAG_SELF_CLOSE", "/")
                    ]),
                ]),
            ]),
        ]))

        result = parse_statement("<div foo={bar} baz=\"foo\" />\n")
        self.assertEqual(result, Tree("start", [
            Tree("statements", [
                Tree("statement", [
                    Tree("jsx_tag_start", [
                        Token("TAG_NAME", "div"),
                        Tree("statement", [
                            Tree("jsx_attribute", [
                                Tree("variable", [
                                    Token("VARIABLE_NAME", "foo"),
                                ]),
                                Tree("statement", [
                                    Tree("variable", [
                                        Token("VARIABLE_NAME", "bar"),
                                    ]),
                                ]),
                            ]),
                        ]),
                        Tree("statement", [
                            Tree("jsx_attribute", [
                                Tree("variable", [
                                    Token("VARIABLE_NAME", "baz"),
                                ]),
                                Tree("statement", [
                                    Tree("string", [
                                        Token("STRING_CONTENTS_DOUBLE", "foo"),
                                    ]),
                                ]),
                            ]),
                        ]),
                        Tree("statement", [Tree("jsx_tag_end", [])]),
                        Token("TAG_SELF_CLOSE", "/")
                    ]),
                ]),
            ]),
        ]))
        
        tree = parse_statement("<input\n/>\n")
        self.assertEqual(tree, _get_start([
            Tree("statement", [
                Tree("jsx_tag_start", [
                    Token("TAG_NAME", "input"),
                    Tree("statement", [Tree("jsx_tag_end", [])]),
                    Token("TAG_SELF_CLOSE", "/"),
                ]),
            ]),
        ]))

        tree = parse_statement("<div>\n    <span>foo</span>\n</div>")
        self.assertEqual(tree, _get_start([
            Tree("statement", [
                Tree("jsx_tag_start", [
                    Token("TAG_NAME", "div"),
                    Tree("statement", [Tree("jsx_tag_end", [])]),
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
                        Tree("jsx_tag_start", [
                            Token("TAG_NAME", "span"),
                            Tree("statement", [
                                Tree("jsx_tag_end", []),
                            ]),
                            Tree("statement", [
                                Tree("variable", [
                                    Token("VARIABLE_NAME", "foo"),
                                ]),
                            ]),
                            Tree("statement", [
                                Tree("jsx_end_tag", [
                                    Token("TAG_NAME", "span"),
                                ]),
                            ]),
                        ]),
                    ]),
                    Tree("statement", [
                        Tree("jsx_end_tag", [
                            Token("TAG_NAME", "div"),
                        ]),
                    ]),
                ]),
            ]),
        ]))
        
    def test_return(self):
        result = parse_statement("function foo()\n\treturn bar\n")
        self.assertEqual(result, Tree("start", [
            Tree("statements", [
                Tree("statement", [
                    Tree("function_definition", [
                        Tree("function_name", [
                            Tree("variable", [Token("VARIABLE_NAME", "foo")]),
                        ]),
                        Tree("nested", [
                            Tree("statement", [
                                Tree("spaces", [Token("TAB", "\t")]),
                                Tree("return_stmt", [
                                    Tree("statement", [
                                        Tree("variable", [
                                            Token("VARIABLE_NAME", "bar"),
                                        ]),
                                    ]),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]))
        
    def test_return_and_jsx(self):
        result = parse_statement("return <div\n>\n</div>\n")
        self.assertEqual(result, Tree("start", [
            Tree("statements", [
                Tree("statement", [
                    Tree("return_stmt", [
                        Tree("statement", [
                            Tree("jsx_tag_start", [
                                Token("TAG_NAME", "div"),
                                Tree("statement", [Tree("jsx_tag_end", [])]),
                                Tree("statement", [
                                    Tree("jsx_end_tag", [Token("TAG_NAME", "div")]),
                                ]), 
                            ]),
                        ]),
                    ]),
                ]),
                Token("NEWLINE", "\n"),
            ]),
        ]))

    def test_value_manipulation(self):
        tree = parse_statement("bar + baz")
        self.assertEqual(tree, _get_start([
            Tree("statement", [
                Tree("value_manipulation", [
                    Tree("statement", [
                        Tree("variable", [
                            Token("VARIABLE_NAME", "bar"),
                        ]),
                    ]),
                    Token("OPERATOR", "+"),
                    Tree("statement", [
                        Tree("variable", [
                            Token("VARIABLE_NAME", "baz"),
                        ]),
                    ]),
                ]),
            ]),
        ]))

        tree = parse_statement("bar    -    \"string\"")
        self.assertEqual(tree, _get_start([
            Tree("statement", [
                Tree("value_manipulation", [
                    Tree("statement", [
                        Tree("variable", [
                            Token("VARIABLE_NAME", "bar"),
                        ]),
                    ]),
                    Token("OPERATOR", "-"),
                    Tree("statement", [
                        Tree("string", [
                            Token("STRING_CONTENTS_DOUBLE", "string"),
                        ]),
                    ]),
                ]),
            ]),
        ]))

        tree = parse_statement("bar + baz + 'foo'")
        self.assertEqual(tree, _get_start([
            Tree("statement", [
                Tree("value_manipulation", [
                    Tree("statement", [
                        Tree("variable", [
                            Token("VARIABLE_NAME", "bar"),
                        ]),
                    ]),
                    Token("OPERATOR", "+"),
                    Tree("statement", [
                        Tree("value_manipulation", [
                            Tree("statement", [
                                Tree("variable", [
                                    Token("VARIABLE_NAME", "baz"),
                                ]),
                            ]),
                            Token("OPERATOR", "+"),
                            Tree("statement", [
                                Tree("string", [
                                    Token("STRING_CONTENTS_SINGLE", "foo"),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]))

    def test_one_line_function(self):
        tree = parse_statement("foo = bar()")
        self.assertEqual(tree, _get_start([
            Tree("statement", [
                Tree("variable_assignment", [
                    Tree("variable", [Token("VARIABLE_NAME", "foo")]),
                    Tree("statement", [
                        Tree("call_function", [
                            Tree("function_name", [
                                Tree('statement', [
                                    Tree("variable", [Token("VARIABLE_NAME", "bar")]),
                                ]),
                            ]),
                            Tree("function_params", []),
                        ]),
                    ]),
                ]),
            ]),
        ]))

    def test_array_indexing(self):
        tree = parse_statement("foo[5]")
        self.assertEqual(tree, _get_start([
            Tree("statement", [
                Tree("array_object_indexing", [
                    Tree("left_hand", [
                        Tree("statement", [
                            Tree("variable", [
                                Token("VARIABLE_NAME", "foo"),
                            ]),
                        ]),
                    ]),
                    Tree("index", [
                        Tree("statement", [
                            Token("NUMBER", "5"),
                        ]),
                    ]),
                ]),
            ]),
        ]))
        
    def test_else(self):
        tree = parse_statement("if foo == true\nelse\n")
        self.assertEqual(tree, _get_start([
            Tree("statement", [
                Tree("if_stat", [
                    Tree("condition", [
                        Tree("statement", [
                            Tree("variable", [
                                Token("VARIABLE_NAME", "foo"),
                            ]),
                        ]),
                        Token("EQUALITY", "=="),
                        Tree("statement", [
                            Tree("boolean", [
                                Token("TRUE", "true"),
                            ]),
                        ]),
                    ]),
                    Tree("nested", []),
                ]),
            ]),
            Tree("statement", [
                Tree("else_stat", [
                    Tree("nested", []),
                ]),
            ]),
        ]))

    def test_map_one_line(self):
        tree = parse_statement("{}")
        self.assertEqual(tree, _get_start([
            Tree("statement", [
                Tree("map", []),
            ]),
        ]))

        tree = parse_statement("{  }")
        self.assertEqual(tree, _get_start([
            Tree("statement", [
                Tree("map", []),
            ]),
        ]))
        
    def test_boolean(self):
        tree = parse_statement("foo = false")
        self.assertEqual(tree, _get_start([
            Tree("statement", [
                Tree("variable_assignment", [
                    Tree("variable", [
                        Token("VARIABLE_NAME", "foo"),
                    ]),
                    Tree("statement", [
                        Tree("boolean", [
                            Token("FALSE", "false"),
                        ]),
                    ]),
                ]),
            ]),
        ]))
        
        tree = parse_statement("foo = true")
        self.assertEqual(tree, _get_start([
            Tree("statement", [
                Tree("variable_assignment", [
                    Tree("variable", [
                        Token("VARIABLE_NAME", "foo"),
                    ]),
                    Tree("statement", [
                        Tree("boolean", [
                            Token("TRUE", "true"),
                        ]),
                    ]),
                ]),
            ]),
        ]))

    def test_function_def_after_call(self):
        tree = parse_statement("foo(\n)\n\nfunction bar()")
        self.assertEqual(tree, _get_start([
            Tree("statement", [
                Tree("call_function", [
                    Tree("function_name", [Tree("statement", [
                        Tree("variable", [Token("VARIABLE_NAME", "foo")]),
                    ])]),
                    Tree("function_params", []),
                ]),
            ]),
            Token("NEWLINE", "\n"),
            Token("NEWLINE", "\n"),
            Tree("statement", [
                Tree("function_definition", [
                    Tree("function_name", [Tree("variable", [Token("VARIABLE_NAME", "bar")])]),
                    Tree("nested", []),
                ]),
            ]),
        ]))

    def test_function_and_jsx(self):
        tree = parse_statement("<input\n\tonChange={function(event)\n\t\tfoo()\n\t}\n\tvalue=\"bar\"\n/>")

        self.assertEqual(tree, _get_start([
            Tree("statement", [
                Tree("jsx_tag_start", [
                    Token("TAG_NAME", "input"),
                    Tree("statement", [
                        Tree("jsx_attribute", [
                            Tree("variable", [Token("VARIABLE_NAME", "onChange")]),
                            Tree("statement", [
                                Tree("function_definition", [
                                    Tree("param", [
                                        Tree("variable", [Token("VARIABLE_NAME", "event")]),
                                    ]),
                                    Tree("nested", [
                                        Tree("statement", [
                                            Tree("spaces", [Token("TAB", "\t")]),
                                            Tree("spaces", [Token("TAB", "\t")]),
                                            Tree("call_function", [
                                                Tree("function_name", [
                                                    Tree("statement", [
                                                        Tree("spaces", [Token("TAB", "\t")]),
                                                        Tree("spaces", [Token("TAB", "\t")]),
                                                        Tree("variable", [Token("VARIABLE_NAME", "foo")]),
                                                    ]),
                                                ]),
                                                Tree("function_params", [])
                                            ]),
                                        ]),
                                    ]),
                                ]),
                            ]),
                        ]),
                    ]),
                    Tree("statement", [
                        Tree("jsx_attribute", [
                            Tree("variable", [Token("VARIABLE_NAME", "value")]),
                            Tree("statement", [
                                Tree("string", [Token("STRING_CONTENTS_DOUBLE", "bar")]),
                            ]),
                        ]),
                    ]),
                    Tree("statement", [
                        Tree("jsx_tag_end", []),
                    ]),
                    Token("TAG_SELF_CLOSE", "/"),
                ]),
            ]),
        ]))

    def test_nesting(self):
        tree = parse_statement("for foo as bar\n\tfoo = bar")

        self.assertEqual(tree, Tree("start", [
            Tree("statements", [
                Tree("statement", [
                    Tree("for_stat", [
                        Tree("for_array", [
                            Tree("variable", [
                                Token("VARIABLE_NAME", "foo"),
                            ]),
                            Tree("variable", [
                                Token("VARIABLE_NAME", "bar"),
                            ]),
                        ]),
                        Tree("nested", [
                            Tree("statement", [
                                Tree("spaces", [
                                    Token("TAB", "	"),
                                ]),
                                Tree("variable_assignment", [
                                    Tree("variable", [
                                        Token("VARIABLE_NAME", "foo"),
                                    ]),
                                    Tree("statement", [
                                        Tree("variable", [
                                            Token("VARIABLE_NAME", "bar"),
                                        ]),
                                    ]),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]))

        tree = parse_statement("function foo()\n\treturn bar")

        self.assertEqual(tree, Tree("start", [
            Tree("statements", [
                Tree("statement", [
                    Tree("function_definition", [
                        Tree("function_name", [
                            Tree("variable", [Token("VARIABLE_NAME", "foo")]),
                        ]),
                        Tree("nested", [
                            Tree("statement", [
                                Tree("spaces", [Token("TAB", "\t")]),
                                Tree("return_stmt", [
                                    Tree("statement", [
                                        Tree("variable", [Token("VARIABLE_NAME", "bar")]),
                                    ]),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]))

        tree = parse_statement("while foo > bar\n\tfoo = bar")

        self.assertEqual(tree, _get_start([
            Tree("statement", [
                Tree("while_stat", [
                    Tree("condition", [
                        Tree("statement", [
                            Tree("variable", [
                                Token("VARIABLE_NAME", "foo"),
                            ]),
                        ]),
                        Token("EQUALITY", ">"),
                        Tree("statement", [
                            Tree("variable", [
                                Token("VARIABLE_NAME", "bar"),
                            ]),
                        ]),
                    ]),
                    Tree("nested", [
                        Tree("statement", [
                            Tree("spaces", [
                                Token("TAB", "	"),
                            ]),
                            Tree("variable_assignment", [
                                Tree("variable", [
                                    Token("VARIABLE_NAME", "foo"),
                                ]),
                                Tree("statement", [
                                    Tree("variable", [
                                        Token("VARIABLE_NAME", "bar"),
                                    ]),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]))

        tree = parse_statement("if true\n\tfoo = bar\nelse\n\tbar = foo")
        
        self.assertEqual(tree, _get_start([
            Tree("statement", [
                Tree("if_stat", [
                    Tree("boolean", [
                        Token("TRUE", "true"),
                    ]),
                    Tree("nested", [
                        Tree("statement", [
                            Tree("spaces", [
                                Token("TAB", "	"),
                            ]),
                            Tree("variable_assignment", [
                                Tree("variable", [
                                    Token("VARIABLE_NAME", "foo"),
                                ]),
                                Tree("statement", [
                                    Tree("variable", [
                                        Token("VARIABLE_NAME", "bar"),
                                    ]),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
            Tree("statement", [
                Tree("else_stat", [
                    Tree("nested", [
                        Tree("statement", [
                            Tree("spaces", [
                                Token("TAB", "	"),
                            ]),
                            Tree("variable_assignment", [
                                Tree("variable", [
                                    Token("VARIABLE_NAME", "bar"),
                                ]),
                                Tree("statement", [
                                    Tree("variable", [
                                        Token("VARIABLE_NAME", "foo"),
                                    ]),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]))

        tree = parse_statement("class Foo\n\tfunction bar()\n\t\tfoo = bar")

        self.assertEqual(tree, _get_start([
            Tree("statement", [
                Tree("class_stat", [
                    Tree("variable", [
                        Token("VARIABLE_NAME", "Foo"),
                    ]),
                    Tree("nested", [
                        Tree("statement", [
                            Tree("spaces", [
                                Token("TAB", "	"),
                            ]),
                            Tree("function_definition", [
                                Tree("function_name", [
                                    Tree("variable", [Token("VARIABLE_NAME", "bar")]),
                                ]),
                                Tree("nested", [
                                     Tree("statement", [
                                        Tree("spaces", [
                                            Token("TAB", "	"),
                                        ]),
                                        Tree("spaces", [
                                            Token("TAB", "	"),
                                        ]),
                                        Tree("variable_assignment", [
                                            Tree("variable", [
                                                Token("VARIABLE_NAME", "foo"),
                                            ]),
                                            Tree("statement", [
                                                Tree("variable", [
                                                    Token("VARIABLE_NAME", "bar"),
                                                ]),
                                            ]),
                                        ]),
                                    ]),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]))

    def test_variable_chain_as_function_param(self):
        tree = parse_statement("foo(\n\tbar.baz\n)")

        self.assertEqual(tree, _get_start([
            Tree("statement", [
                Tree("call_function", [
                    Tree("function_name", [
                        Tree("statement", [
                            Tree("variable", [
                                Token("VARIABLE_NAME", "foo"),
                            ]),
                        ]),
                    ]),
                    Tree("function_params", [
                        Token("NEWLINE", "\n"),
                        Tree("statement", [
                            Tree("spaces", [
                                Token("TAB", "\t"),
                            ]),
                            Tree("variable", [
                                Tree("instance_variable_chain", [
                                    Token("VARIABLE_NAME", "bar"),
                                    Token("VARIABLE_NAME", "baz"),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ])
        ]))

    def test_key_after_function_in_map(self):
        tree = parse_statement("foo = {\n\tonChange: function(event)\n\t\tfoo()\n\tvalue: \"bar\"\n")

        self.assertEqual(tree, _get_start([
            Tree("statement", [
                Tree("variable_assignment", [
                    Tree("variable", [
                        Token("VARIABLE_NAME", "foo"),
                    ]),
                    Tree("statement", [
                        Tree("map", [
                            Tree("statement", [
                                Tree("map_row", [
                                    Token("VARIABLE_NAME", "onChange"),
                                    Tree("statement", [
                                        Tree("function_definition", [
                                            Tree("param", [
                                                Tree("variable", [
                                                    Token("VARIABLE_NAME", "event"),
                                                ])
                                            ]),
                                            Tree("nested", [
                                                Tree("statement", [
                                                    Tree("spaces", [
                                                        Token("TAB", "	"),
                                                    ]),
                                                    Tree("spaces", [
                                                        Token("TAB", "	"),
                                                    ]),
                                                    Tree("call_function", [
                                                        Tree("function_name", [
                                                            Tree("statement", [
                                                                Tree("spaces", [
                                                                    Token("TAB", "	"),
                                                                ]),
                                                                Tree("spaces", [
                                                                    Token("TAB", "	"),
                                                                ]),
                                                                Tree("variable", [
                                                                    Token("VARIABLE_NAME", "foo"),
                                                                ]),
                                                            ]),
                                                        ]),
                                                        Tree("function_params", []),
                                                    ]),
                                                ]),
                                            ]),
                                        ]),
                                    ]),
                                ]),
                            ]),
                            Tree("statement", [
                                Tree("map_row", [
                                    Token("VARIABLE_NAME", "value"),
                                    Tree("statement", [
                                        Tree("string", [
                                            Token("STRING_CONTENTS_DOUBLE", "bar"),
                                        ]),
                                    ]),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]))

    def test_value_after_function_in_array(self):
        tree = parse_statement("foo = [\n\tfunction(event)\n\t\tfoo()\n\t\"bar\"\n]")
        self.assertEqual(tree, _get_start([
            Tree("statement", [
                Tree("variable_assignment", [
                    Tree("variable", [
                        Token("VARIABLE_NAME", "foo"),
                    ]),
                    Tree("statement", [
                        Tree("array", [
                            Tree("statement", [
                                Tree("spaces", [
                                    Token("TAB", "	"),
                                ]),
                                Tree("function_definition", [
                                    Tree("param", [
                                        Tree("variable", [
                                            Token("VARIABLE_NAME", "event"),
                                        ]),
                                    ]),
                                    Tree("nested", [
                                        Tree("statement", [
                                            Tree("spaces", [
                                                Token("TAB", "	"),
                                            ]),
                                            Tree("spaces", [
                                                Token("TAB", "	"),
                                            ]),
                                            Tree("call_function", [
                                                Tree("function_name", [
                                                    Tree("statement", [
                                                        Tree("spaces", [
                                                            Token("TAB", "	"),
                                                        ]),
                                                        Tree("spaces", [
                                                            Token("TAB", "	"),
                                                        ]),
                                                        Tree("variable", [
                                                            Token("VARIABLE_NAME", "foo"),
                                                        ]),
                                                    ]),
                                                ]),
                                                Tree("function_params", []),
                                            ]),
                                        ]),
                                    ]),
                                ]),
                            ]),
                            Tree("statement", [
                                Tree("spaces", [
                                    Token("TAB", "	"),
                                ]),
                                Tree("string", [
                                    Token("STRING_CONTENTS_DOUBLE", "bar"),
                                ]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]))

if __name__ == "__main__":
    unittest.main()