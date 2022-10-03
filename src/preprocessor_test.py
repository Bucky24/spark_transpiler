import unittest

if 'unittest.util' in __import__('sys').modules:
    # Show full diff in self.assertEqual.
    __import__('sys').modules['unittest.util']._MAX_LENGTH = 999999999

from grammar import parse_statement
from transformer import process_tree, TYPES
from preprocessor import preprocess
from utils import print_tree

def statement(data, spaces):
    return {
        "type": TYPES["STATEMENT"],
        "spaces": spaces,
        "statement": data,
    }

def block(statement, children):
    return {
        "type": TYPES['BLOCK'],
        "statement": statement,
        "children": children,
    }

class TestPreprocessor(unittest.TestCase):
    def test_frontend_pragma(self):
        tree = parse_statement("#frontend\nfoo = 'abcd'")
        processed = process_tree(tree)
        preprocessed = preprocess(processed)

        self.assertEqual(preprocessed['backend'], [])
        self.assertEqual(preprocessed['frontend'],[
            statement({
                "type": TYPES['VARIABLE_ASSIGNMENT'],
                "name": "foo",
                "value": statement('"abcd"', 0),
            }, 0)
        ])

    def test_backend_pragma(self):
        tree = parse_statement("#backend\nfoo = 'abcd'")
        processed = process_tree(tree)
        preprocessed = preprocess(processed)

        self.assertEqual(preprocessed['frontend'], [])
        self.assertEqual(preprocessed['backend'],[
            statement({
                "type": TYPES['VARIABLE_ASSIGNMENT'],
                "name": "foo",
                "value": statement('"abcd"', 0),
            }, 0)
        ])

    def test_default_env(self):
        tree = parse_statement("foo = 'abcd'")
        processed = process_tree(tree)
        preprocessed = preprocess(processed)

        self.assertEqual(preprocessed['frontend'], [])
        self.assertEqual(preprocessed['backend'],[
            statement({
                "type": TYPES['VARIABLE_ASSIGNMENT'],
                "name": "foo",
                "value": statement('"abcd"', 0),
            }, 0)
        ])

    def test_mixed_env(self):
        tree = parse_statement("#frontend\nfoo = 'abcd'\n#backend\nbar = '123'\n#frontend\nbin = foo")
        processed = process_tree(tree)
        preprocessed = preprocess(processed)

        self.assertEqual(preprocessed['frontend'], [
            statement({
                "type": TYPES['VARIABLE_ASSIGNMENT'],
                "name": "foo",
                "value": statement('"abcd"', 0),
            }, 0),
            statement({
                "type": TYPES['VARIABLE_ASSIGNMENT'],
                "name": "bin",
                "value": statement('foo', 0),
            }, 0)
        ])
        self.assertEqual(preprocessed['backend'],[
            statement({
                "type": TYPES['VARIABLE_ASSIGNMENT'],
                "name": "bar",
                "value": statement('"123"', 0),
            }, 0)
        ])

    def test_for_nesting(self):
        tree = parse_statement("for a as b\n\tfoo = bar\nbar=baz")
        processed = process_tree(tree)
        preprocessed = preprocess(processed)

        self.assertEqual(preprocessed['backend'], [
            {
                "type": TYPES['BLOCK'],
                "statement": statement({
                    "type": TYPES['FOR_OF'],
                    "variable": "a",
                    "value": "b",
                }, 0),
                "children": [statement({
                    "type": TYPES['VARIABLE_ASSIGNMENT'],
                    "name": "foo",
                    "value": statement("bar", 0),
                }, 4)]
            },
            statement({
                "type": TYPES['VARIABLE_ASSIGNMENT'],
                "name": "bar",
                "value": statement("baz", 0),
            }, 0)
        ])

    def test_multi_level_nesting(self):
        tree = parse_statement("for a as b\n\tfor b as a\n\t\tfoo = bar\n\tbar=baz\na=b")
        processed = process_tree(tree)
        preprocessed = preprocess(processed)

        self.assertEqual(preprocessed['backend'], [
            block(
                statement({
                    "type": TYPES['FOR_OF'],
                    "variable": "a",
                    "value": "b",
                }, 0),
                [
                    block(
                        statement({
                            "type": TYPES['FOR_OF'],
                            "variable": "b",
                            "value": "a",
                        }, 4),
                        [
                            statement({
                                "type": TYPES['VARIABLE_ASSIGNMENT'],
                                "name": "foo",
                                "value": statement("bar", 0),
                            }, 8)
                        ],
                    ),
                    statement({
                        "type": TYPES['VARIABLE_ASSIGNMENT'],
                        "name": "bar",
                        "value": statement("baz", 0),
                    }, 4)
                ]
            ),
            statement({
                "type": TYPES['VARIABLE_ASSIGNMENT'],
                "name": "a",
                "value": statement("b", 0),
            }, 0)
        ])

    def test_if_nesting(self):
        tree = parse_statement("if a == b\n\tfoo = bar\nbar=baz")
        processed = process_tree(tree)
        preprocessed = preprocess(processed)

        self.assertEqual(preprocessed['backend'], [
            {
                "type": TYPES['BLOCK'],
                "statement": statement({
                    "type": TYPES['IF'],
                    "condition": {
                        "type": TYPES['CONDITION'],
                        "left_hand": statement("a", 0),
                        "right_hand": statement("b", 0),
                        "condition": "==",
                    },
                }, 0),
                "children": [statement({
                    "type": TYPES['VARIABLE_ASSIGNMENT'],
                    "name": "foo",
                    "value": statement("bar", 0),
                }, 4)]
            },
            statement({
                "type": TYPES['VARIABLE_ASSIGNMENT'],
                "name": "bar",
                "value": statement("baz", 0),
            }, 0)
        ])

    def test_while_nesting(self):
        tree = parse_statement("while a == b\n\tfoo = bar\nbar=baz")
        processed = process_tree(tree)
        preprocessed = preprocess(processed)

        self.assertEqual(preprocessed['backend'], [
            {
                "type": TYPES['BLOCK'],
                "statement": statement({
                    "type": TYPES['WHILE'],
                    "condition": {
                        "type": TYPES['CONDITION'],
                        "left_hand": statement("a", 0),
                        "right_hand": statement("b", 0),
                        "condition": "==",
                    },
                }, 0),
                "children": [statement({
                    "type": TYPES['VARIABLE_ASSIGNMENT'],
                    "name": "foo",
                    "value": statement("bar", 0),
                }, 4)]
            },
            statement({
                "type": TYPES['VARIABLE_ASSIGNMENT'],
                "name": "bar",
                "value": statement("baz", 0),
            }, 0)
        ])

    def test_function_nesting(self):
        tree = parse_statement("function(a, b)\n\tfoo = bar\nbar=baz")
        processed = process_tree(tree)
        preprocessed = preprocess(processed)

        self.assertEqual(preprocessed['backend'], [
            {
                "type": TYPES['BLOCK'],
                "statement": statement({
                    "type": TYPES['FUNCTION'],
                    "name": None,
                    "params": ["a", "b"],
                }, 0),
                "children": [statement({
                    "type": TYPES['VARIABLE_ASSIGNMENT'],
                    "name": "foo",
                    "value": statement("bar", 0),
                }, 4)]
            },
            statement({
                "type": TYPES['VARIABLE_ASSIGNMENT'],
                "name": "bar",
                "value": statement("baz", 0),
            }, 0)
        ])

    def test_class_nesting(self):
        tree = parse_statement("class Foo\n\tfunction Foo()\n\t\tfoo = bar")
        processed = process_tree(tree)
        preprocessed = preprocess(processed)

        self.assertEqual(preprocessed['backend'], [
            {
                "type": TYPES['BLOCK'],
                "statement": statement({
                    "type": TYPES['CLASS'],
                    "name": "Foo",
                    "extends": None,
                }, 0),
                "children": [{
                    "type": TYPES['BLOCK'],
                    "statement": statement({
                        "type": TYPES['FUNCTION'],
                        "name": "Foo",
                        "params": [],
                    }, 4),
                    "children": [statement({
                        "type": TYPES['VARIABLE_ASSIGNMENT'],
                        "name": "foo",
                        "value": statement("bar", 0)
                    }, 8)],
                }]
            },
        ])

    def test_backend_import_function(self):
        tree = parse_statement("print(\n    'foo'\n)")
        processed = process_tree(tree)
        preprocessed = preprocess(processed)
        
        self.assertEqual(preprocessed['backend_imports'], {'stdlib': ['print']})

    def test_frontend_import_function(self):
        tree = parse_statement("#frontend\nprint(\n    'foo'\n)")
        processed = process_tree(tree)
        preprocessed = preprocess(processed)
        
        self.assertEqual(preprocessed['frontend_imports'], {'stdlib': ['print']})

    def test_backend_blocks_then_frontend(self):
        tree = parse_statement("if foo == bar\n    if bar == baz\n        foo = bar\n#frontend\nfoo = bar\n")
        processed = process_tree(tree)
        preprocessed = preprocess(processed)
        self.assertEqual(preprocessed['backend'], [
            {
                "type": TYPES["BLOCK"],
                "statement": statement({
                    "type": TYPES["IF"],
                    "condition": {
                        "type": TYPES["CONDITION"],
                        "left_hand": statement('foo', 0),
                        "condition": "==",
                        "right_hand": statement('bar', 0),
                    },
                }, 0),
                "children": [
                    {
                        "type": TYPES["BLOCK"],
                        "statement": statement({
                            "type": TYPES["IF"],
                            "condition": {
                                "type": TYPES["CONDITION"],
                                "left_hand": statement("bar", 0),
                                "condition": "==",
                                "right_hand": statement('baz', 0),
                            },
                        }, 4),
                        "children": [
                            statement({
                                "type": TYPES["VARIABLE_ASSIGNMENT"],
                                "name": "foo",
                                "value": statement("bar", 0),
                            }, 8),
                        ],
                    }
                ],
            },
        ])

        self.assertEqual(preprocessed['frontend'], [statement({
            "type": TYPES["VARIABLE_ASSIGNMENT"],
            "name": "foo",
            "value": statement("bar", 0),
        }, 0)])

if __name__ == "__main__":
    unittest.main()