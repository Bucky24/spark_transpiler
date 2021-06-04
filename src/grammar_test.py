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
                    ]),
                ]),
                Token("NEWLINE", "\n"),
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
                Token("NEWLINE", "\n"),
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

        result = parse_statement("foo(\n  a\n  b\n)\n")
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
                            Tree("array_start", []),
                        ]),
                    ]),
                ]),
                Token("NEWLINE", "\n"),
                Tree("statement", [
                    Tree("spaces", [Token("TAB", "\t")]),
                    Tree("string", [Token("STRING_CONTENTS_SINGLE", "bar")])
                ]),
                Token("NEWLINE", "\n"),
                Tree("statement", [
                    Tree("spaces", [Token("TAB", "\t")]),
                    Tree("string", [Token("STRING_CONTENTS_SINGLE", "baz")])
                ]),
                Token("NEWLINE", "\n"),
                Tree("statement", [
                    Tree("array_end", []),
                ]),
                Token("NEWLINE", "\n"),
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
                            Tree("map_start", [])
                        ])
                    ])
                ]),
                Token("NEWLINE", "\n"),
                Tree("statement", [
                    Tree("spaces", [Token("TAB", "\t")]),
                    Tree("map_row", [
                        Token("VARIABLE_NAME", "abcd"),
                        Tree("statement_no_space", [
                            Tree("string", [
                                Token("STRING_CONTENTS_SINGLE", "foo"),
                            ]),
                        ]),
                    ]),
                ]),
                Token("NEWLINE", "\n"),
                Tree("statement", [
                    Tree("map_end", []),
                ]),
                Token("NEWLINE", "\n"),
            ]),
        ]))
        
    def test_nested_map_array(self):
        result = parse_statement("foo = {\n\t[\n\t\t{\n\t\t\tfoo: 'bar'\n\t\t}\n\t]\n}\n")
        self.assertEqual(result, Tree("start", [
            Tree("statements", [
                Tree("statement", [
                    Tree("variable_assignment", [
                        Tree("variable", [Token("VARIABLE_NAME", "foo")]),
                        Tree("statement", [
                            Tree("map_start", [])
                        ])
                    ])
                ]),
                Token("NEWLINE", "\n"),
                Tree("statement", [
                    Tree("spaces", [Token("TAB", "\t")]),
                    Tree("array_start", []),
                ]),
                Token("NEWLINE", "\n"),
                Tree("statement", [
                    Tree("spaces", [Token("TAB", "\t")]),
                    Tree("spaces", [Token("TAB", "\t")]),
                    Tree("map_start", []),
                ]),
                Token("NEWLINE", "\n"),
                Tree("statement", [
                    Tree("spaces", [Token("TAB", "\t")]),
                    Tree("spaces", [Token("TAB", "\t")]),
                    Tree("spaces", [Token("TAB", "\t")]),
                    Tree("map_row", [
                        Token("VARIABLE_NAME", "foo"),
                        Tree("statement_no_space", [
                            Tree("string", [
                                Token("STRING_CONTENTS_SINGLE", "bar"),
                            ]),
                        ]),
                    ]),
                ]),
                Token("NEWLINE", "\n"),
                Tree("statement", [
                    Tree("spaces", [Token("TAB", "\t")]),
                    Tree("spaces", [Token("TAB", "\t")]),
                    Tree("map_end", []),
                ]),
                Token("NEWLINE", "\n"),
                Tree("statement", [
                    Tree("spaces", [Token("TAB", "\t")]),
                    Tree("array_end", []),
                ]),
                Token("NEWLINE", "\n"),
                Tree("statement", [
                    Tree("map_end", []),
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
                        Tree("jsx_tag_end", []),
                    ]),
                ]),
                Token("NEWLINE", "\n"),
                Tree("statement", [
                    Tree("jsx_end", [
                        Token("TAG_NAME", "div"),
                    ])
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
                        Token("TAG_SELF_CLOSE", "/"),
                        Tree("jsx_tag_end", []),
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
                    ]),
                ]),
                Token("NEWLINE", "\n"),
                Tree("statement", [
                    Tree("spaces", [Token("TAB", "\t")]),
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
                Tree("statement", [
                    Tree("jsx_tag_end", [])
                ]),
                Token("NEWLINE", "\n"),
                Tree("statement", [
                    Tree("jsx_end", [
                        Token("TAG_NAME", "div"),
                    ])
                ]),
                Token("NEWLINE", "\n"),
            ]),
        ]))
        
        tree = parse_statement("<input\n/>\n")
        self.assertEqual(tree, _get_start([
            Tree("statement", [
                Tree("jsx_tag_start", [
                    Token("TAG_NAME", "input")
                ]),
            ]),
            Token("NEWLINE", "\n"),
            Tree("statement", [
                Tree("jsx_tag_end", [
                    Token("TAG_SELF_CLOSE", "/"),
                ]),
            ]),
            Token("NEWLINE", "\n"),
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
                    ]),
                ]),
                Token("NEWLINE", "\n"),
                Tree("statement", [
                    Tree("spaces", [Token("TAB", "\t")]),
                    Tree("return_stmt", [
                        Tree("statement_no_space", [
                            Tree("variable", [
                                Token("VARIABLE_NAME", "bar"),
                            ]),
                        ]),
                    ]),
                ]),
                Token("NEWLINE", "\n"),
            ]),
        ]))
        
    def test_return_and_jsx(self):
        result = parse_statement("return <div\n>\n</div>\n")
        self.assertEqual(result, Tree("start", [
            Tree("statements", [
                Tree("statement", [
                    Tree("return_stmt", [
                        Tree("statement_no_space", [
                            Tree("jsx_tag_start", [
                                Token("TAG_NAME", "div"),
                            ]),
                        ]),
                    ]),
                ]),
                Token("NEWLINE", "\n"),
                Tree("statement", [
                    Tree("jsx_tag_end", []),
                ]), 
                Token("NEWLINE", "\n"),
                Tree("statement", [
                    Tree("jsx_end", [
                        Token("TAG_NAME", "div")
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
                    Tree("statement_no_space_no_value_manip", [
                        Tree("variable", [
                            Token("VARIABLE_NAME", "bar"),
                        ]),
                    ]),
                    Token("OPERATOR", "+"),
                    Tree("statement_no_space_no_value_manip", [
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
                    Tree("statement_no_space_no_value_manip", [
                        Tree("variable", [
                            Token("VARIABLE_NAME", "bar"),
                        ]),
                    ]),
                    Token("OPERATOR", "-"),
                    Tree("statement_no_space_no_value_manip", [
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
                    Tree("statement_no_space_no_value_manip", [
                        Tree("variable", [
                            Token("VARIABLE_NAME", "bar"),
                        ]),
                    ]),
                    Token("OPERATOR", "+"),
                    Tree("statement_no_space_no_value_manip", [
                        Tree("variable", [
                            Token("VARIABLE_NAME", "baz"),
                        ]),
                    ]),
                    Token("OPERATOR", "+"),
                    Tree("statement_no_space_no_value_manip", [
                        Tree("string", [
                            Token("STRING_CONTENTS_SINGLE", "foo"),
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
                        Tree("call_function_one_line", [
                            Tree("variable", [Token("VARIABLE_NAME", "bar")]),
                        ]),
                    ]),
                ]),
            ]),
        ]))

    def test_array_indexing(self):
        tree = parse_statement("foo[5]")
        self.assertEqual(tree, _get_start([
            Tree("statement", [
                Tree("variable", [
                    Token("VARIABLE_NAME", "foo[5]"),
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
                            Tree("variable", [
                                Token("VARIABLE_NAME", "true"),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
            Token("NEWLINE", "\n"),
            Tree("statement", [
                Tree("else_stat", []),
            ]),
            Token("NEWLINE", "\n"),
        ]))

    def test_map_one_line(self):
        tree = parse_statement("{}")
        self.assertEqual(tree, _get_start([
            Tree("statement", [
                Tree("map_one_line", []),
            ]),
        ]))

        tree = parse_statement("{  }")
        self.assertEqual(tree, _get_start([
            Tree("statement", [
                Tree("map_one_line", []),
            ]),
        ]))

if __name__ == "__main__":
    unittest.main()