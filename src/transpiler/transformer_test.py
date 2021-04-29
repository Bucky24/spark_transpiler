import unittest

from grammar import parse_statement
from transformer import process_tree, TYPES

def statement(data, spaces):
    return {
        "type": TYPES["STATEMENT"],
        "spaces": spaces,
        "statement": data,
    }

class TestTransformer(unittest.TestCase):
    def test_variables(self):
        tree = parse_statement("foo = 'string'\nfoo = \"string2\"\nfoo = 124.121\n")
        processed = process_tree(tree)
        self.assertEqual(processed, [
            statement({
                "type": TYPES["VARIABLE_ASSIGNMENT"],
                "name": "foo",
                "value": statement("\"string\"", 0),
            }, 0),
            statement({
                "type": TYPES["VARIABLE_ASSIGNMENT"],
                "name": "foo",
                "value": statement("\"string2\"", 0),
            }, 0),
            statement({
                "type": TYPES["VARIABLE_ASSIGNMENT"],
                "name": "foo",
                "value": statement(124.121, 0),
            }, 0),
        ])

    def test_conditional(self):
        tree = parse_statement("""foo = 'string'
if foo == "string"
    print(
        foo
    )
""")
        processed = process_tree(tree)
        self.assertEqual(processed, [
            statement({
                "type": TYPES["VARIABLE_ASSIGNMENT"],
                "name": "foo",
                "value": statement("\"string\"", 0),
            }, 0),
            statement({
                "type": TYPES["IF"],
                "left_hand": statement("foo", 0),
                "condition": "==",
                "right_hand": statement("\"string\"", 0),
            }, 0),
            statement({
                "type": TYPES["CALL_FUNC"],
                "function": "print",
            }, 4),
            statement("foo", 8),
            statement({
                "type": TYPES["CALL_FUNC_END"],
            }, 4),
        ])

    def test_loops(self):
        tree = parse_statement("""for foo as bar
    foo = bar
for foo as bar : baz
    foo = bar
for i=0;i<5;i++
    foo = i
while foo == bar
    foo = bar
""")
        processed = process_tree(tree)
        self.assertEqual(processed, [
            statement({
                "type": TYPES["FOR_OF"],
                "variable": "foo",
                "value": "bar",
            }, 0),
            statement({
                "type": TYPES["VARIABLE_ASSIGNMENT"],
                "name": "foo",
                "value": statement("bar", 0),
            }, 4),
            statement({
                "type": TYPES["FOR_OF"],
                "variable": "foo",
                "key": "bar",
                "value": "baz",
            }, 0),
            statement({
                "type": TYPES["VARIABLE_ASSIGNMENT"],
                "name": "foo",
                "value": statement("bar", 0),
            }, 4),
            statement({
                "type": TYPES["FOR"],
                "conditions": [
                    statement({
                        "type": TYPES["VARIABLE_ASSIGNMENT"],
                        "name": "i",
                        "value": statement(0, 0),
                    }, 0),
                    statement([
                        statement("i", 0),
                        "<",
                        statement(5, 0),
                    ], 0),
                    statement({
                        "type": TYPES["INCREMENT"],
                        "variable": "i",
                    }, 0),
                ],
            }, 0),
            statement({
                "type": TYPES["VARIABLE_ASSIGNMENT"],
                "name": "foo",
                "value": statement("i", 0),
            }, 4),
            statement({
                "type": TYPES["WHILE"],
                "condition": [
                    statement("foo", 0),
                    "==",
                    statement("bar", 0),
                ],
            }, 0),
            statement({
                "type": TYPES["VARIABLE_ASSIGNMENT"],
                "name": "foo",
                "value": statement("bar", 0),
            }, 4),
        ])

    def test_functions(self):
        tree = parse_statement("""function abba(a, b, c)
    foo = bar
function(a,b,c)
    foo = bar
function abba()
    foo = bar
function()
    foo = bar
""")
        processed = process_tree(tree)
        self.assertEqual(processed, [
            statement({
                "type": TYPES["FUNCTION"],
                "name": "abba",
                "params": ["a", "b", "c"],
            }, 0),
            statement({
                "type": TYPES["VARIABLE_ASSIGNMENT"],
                "name": "foo",
                "value": statement("bar", 0), 
            }, 4),
            statement({
                "type": TYPES["FUNCTION"],
                "name": None,
                "params": ["a", "b", "c"],
            }, 0),
            statement({
                "type": TYPES["VARIABLE_ASSIGNMENT"],
                "name": "foo",
                "value": statement("bar", 0), 
            }, 4),
            statement({
                "type": TYPES["FUNCTION"],
                "name": "abba",
                "params": [],
            }, 0),
            statement({
                "type": TYPES["VARIABLE_ASSIGNMENT"],
                "name": "foo",
                "value": statement("bar", 0), 
            }, 4), 
            statement({
                "type": TYPES["FUNCTION"],
                "name": None,
                "params": [],
            }, 0),
            statement({
                "type": TYPES["VARIABLE_ASSIGNMENT"],
                "name": "foo",
                "value": statement("bar", 0), 
            }, 4),
        ])

    def test_class(self):
        tree = parse_statement("""class foo extends bar
    function abba()
        foo = bar

class bar
    function abba()
        foo = bar
""")
        processed = process_tree(tree)
        self.assertEqual(processed, [
            statement({
                "type": TYPES["CLASS"],
                "name": "foo",
                "extends": "bar",
            }, 0),
            statement({
                "type": TYPES["FUNCTION"],
                "name": "abba",
                "params": [],
            }, 4),
            statement({
                "type": TYPES["VARIABLE_ASSIGNMENT"],
                "name": "foo",
                "value": statement("bar", 0), 
            }, 8),
            statement({
                "type": TYPES["CLASS"],
                "name": "bar",
                "extends": None,
            }, 0),
            statement({
                "type": TYPES["FUNCTION"],
                "name": "abba",
                "params": [],
            }, 4),
            statement({
                "type": TYPES["VARIABLE_ASSIGNMENT"],
                "name": "foo",
                "value": statement("bar", 0), 
            }, 8),
        ])

        tree = parse_statement("foo.bar.baz(\n)\n")
        processed = process_tree(tree)
        self.assertEqual(processed, [
            statement({
                "type": TYPES["CALL_FUNC"],
                "function": {
                    "type": TYPES["VARIABLE_CHAIN"],
                    "chain": ["foo", "bar", "baz"],
                }
            }, 0),
            statement({
                "type": TYPES["CALL_FUNC_END"],
            }, 0),
        ])

if __name__ == "__main__":
    unittest.main()