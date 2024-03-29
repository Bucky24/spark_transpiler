import unittest

if 'unittest.util' in __import__('sys').modules:
    # Show full diff in self.assertEqual.
    __import__('sys').modules['unittest.util']._MAX_LENGTH = 999999999

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
                "condition": {
                    "type": TYPES["CONDITION"],
                    "left_hand": statement("foo", 0),
                    "condition": "==",
                    "right_hand": statement("\"string\"", 0),
                },
                "nested": [
                    statement({
                        "type": TYPES["CALL_FUNC"],
                        "function": {
                            "type": TYPES["FUNCTION_NAME"],
                            "name": statement("print", 4),
                        },
                        "parameters": {
                            'type': TYPES['FUNCTION_PARAMS'],
                            'params': [
                                statement("foo", 0),
                            ],
                        },
                    }, 4),
                ],
            }, 0)
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
                "nested": [
                    statement({
                        "type": TYPES["VARIABLE_ASSIGNMENT"],
                        "name": "foo",
                        "value": statement("bar", 0),
                    }, 4),
                ],
            }, 0),
            statement({
                "type": TYPES["FOR_OF"],
                "variable": "foo",
                "key": "bar",
                "value": "baz",
                "nested": [
                    statement({
                        "type": TYPES["VARIABLE_ASSIGNMENT"],
                        "name": "foo",
                        "value": statement("bar", 0),
                    }, 4),
                ],
            }, 0),
            statement({
                "type": TYPES["FOR"],
                "conditions": [
                    statement({
                        "type": TYPES["VARIABLE_ASSIGNMENT"],
                        "name": "i",
                        "value": statement(0, 0),
                    }, 0),
                    statement({
                        "type": TYPES["CONDITION"],
                        "left_hand": statement("i", 0),
                        "condition": "<",
                        "right_hand": statement(5, 0),
                    }, 0),
                    statement({
                        "type": TYPES["INCREMENT"],
                        "variable": "i",
                    }, 0),
                ],
                "nested": [
                    statement({
                        "type": TYPES["VARIABLE_ASSIGNMENT"],
                        "name": "foo",
                        "value": statement("i", 0),
                    }, 4),
                ],
            }, 0),
            statement({
                "type": TYPES["WHILE"],
                "condition": {
                    "type": TYPES["CONDITION"],
                    "left_hand": statement("foo", 0),
                    "condition": "==",
                    "right_hand": statement("bar", 0),
                },
                "nested": [
                    statement({
                        "type": TYPES["VARIABLE_ASSIGNMENT"],
                        "name": "foo",
                        "value": statement("bar", 0),
                    }, 4),
                ],
            }, 0),
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
                "nested": [
                    statement({
                        "type": TYPES["VARIABLE_ASSIGNMENT"],
                        "name": "foo",
                        "value": statement("bar", 0), 
                    }, 4),
                ],
            }, 0),
            statement({
                "type": TYPES["FUNCTION"],
                "name": None,
                "params": ["a", "b", "c"],
                "nested": [
                    statement({
                        "type": TYPES["VARIABLE_ASSIGNMENT"],
                        "name": "foo",
                        "value": statement("bar", 0), 
                    }, 4),
                ],
            }, 0),
            statement({
                "type": TYPES["FUNCTION"],
                "name": "abba",
                "params": [],
                "nested": [
                    statement({
                        "type": TYPES["VARIABLE_ASSIGNMENT"],
                        "name": "foo",
                        "value": statement("bar", 0), 
                    }, 4),
                ],
            }, 0),
            statement({
                "type": TYPES["FUNCTION"],
                "name": None,
                "params": [],
                "nested": [
                    statement({
                        "type": TYPES["VARIABLE_ASSIGNMENT"],
                        "name": "foo",
                        "value": statement("bar", 0), 
                    }, 4),
                ],
            }, 0),
        ])

        tree = parse_statement("bar = foo(\n)\n")
        processed = process_tree(tree)
        self.assertEqual(processed, [
            statement({
                "type": TYPES['VARIABLE_ASSIGNMENT'],
                "name": "bar",
                "value": statement({
                    "type": TYPES["CALL_FUNC"],
                    "function": {
                        "type": TYPES['FUNCTION_NAME'],
                        "name": statement("foo", 0),
                    },
                    "parameters": {
                        "type": TYPES['FUNCTION_PARAMS'],
                        "params": [],
                    },
                }, 0),
            }, 0),
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
                "nested": [
                    statement({
                        "type": TYPES["FUNCTION"],
                        "name": "abba",
                        "params": [],
                        "nested": [statement({
                            "type": TYPES["VARIABLE_ASSIGNMENT"],
                            "name": "foo",
                            "value": statement("bar", 0), 
                        }, 8)]
                    }, 4),
                ],
            }, 0),
            
            statement({
                "type": TYPES["CLASS"],
                "name": "bar",
                "extends": None,
                "nested": [
                    statement({
                        "type": TYPES["FUNCTION"],
                        "name": "abba",
                        "params": [],
                        "nested": [statement({
                            "type": TYPES["VARIABLE_ASSIGNMENT"],
                            "name": "foo",
                            "value": statement("bar", 0), 
                        }, 8)],
                    }, 4),
                ],
            }, 0),
        ])

        tree = parse_statement("foo.bar.baz(\n)\n")
        processed = process_tree(tree)
        self.assertEqual(processed, [
            statement({
                "type": TYPES["CALL_FUNC"],
                "function": {
                    'type': TYPES['FUNCTION_NAME'],
                    'name': statement({
                        "type": TYPES["VARIABLE_CHAIN"],
                        "chain": ["foo", "bar", "baz"],
                    }, 0),
                },
                "parameters": {
                    'type': TYPES['FUNCTION_PARAMS'],
                    "params": [],
                } ,
            }, 0),
        ])

    def test_pragma(self):
        tree = parse_statement("#FRONTEND")
        processed = process_tree(tree)
        self.assertEqual(processed, [
            statement({
                "type": TYPES["PRAGMA"],
                "pragma": "FRONTEND",
            }, 0),
        ])
        
        tree = parse_statement("#foo bar")
        processed = process_tree(tree)
        self.assertEqual(processed, [
            statement({
                "type": TYPES["PRAGMA"],
                "pragma": "foo",
                "values": ["bar"],
            }, 0),
        ])

        tree = parse_statement("#foo bar,baz")
        processed = process_tree(tree)
        self.assertEqual(processed, [
            statement({
                "type": TYPES["PRAGMA"],
                "pragma": "foo",
                "values": ["bar", "baz"],
            }, 0),
        ])
        
    def test_tabs_and_spaces(self):
        tree = parse_statement("foo = bar\n    foo = bar\n\tfoo = bar\n")
        processed = process_tree(tree)
        self.assertEqual(processed, [
            statement({
                "type": TYPES["VARIABLE_ASSIGNMENT"],
                "name": "foo",
                "value": statement("bar", 0),
            }, 0),
            statement({
                "type": TYPES["VARIABLE_ASSIGNMENT"],
                "name": "foo",
                "value": statement("bar", 0),
            }, 4),
            statement({
                "type": TYPES["VARIABLE_ASSIGNMENT"],
                "name": "foo",
                "value": statement("bar", 0),
            }, 4),
        ])
        
    def test_arrays(self):
        tree = parse_statement("foo = [\n\t'bar'\n\t'baz'\n]\n")
        processed = process_tree(tree)
        self.assertEqual(processed, [
            statement({
                "type": TYPES["VARIABLE_ASSIGNMENT"],
                "name": "foo",
                "value": statement({
                    "type": TYPES["ARRAY"],
                    "children": [
                        statement("\"bar\"", 4),
                        statement("\"baz\"", 4),
                    ]
                }, 0),
            }, 0),
        ])
        
    def test_maps(self):
        tree = parse_statement("foo = {\n\tabcd: 'foo'\n}\n")
        processed = process_tree(tree)
        self.assertEqual(processed, [
            statement({
                "type": TYPES["VARIABLE_ASSIGNMENT"],
                "name": "foo",
                "value": statement({
                    "type": TYPES["MAP"],
                    "children": [
                        statement({
                            "type": TYPES["MAP_ROW"],
                            "key": "abcd",
                            "value": statement("\"foo\"", 0),
                        }, 0),
                    ],
                }, 0),
            }, 0),
        ])
        
    def test_jsx(self):
        tree = parse_statement("<div>\n</div>\n")
        processed = process_tree(tree)
        self.assertEqual(processed, [
            statement({
                "type": TYPES["JSX_START_TAG"],
                "tag": "div",
                "self_closes": False,
                "attributes": [],
                "children": [],
            }, 0),
        ])
        
        tree = parse_statement("<div/>")
        processed = process_tree(tree)
        self.assertEqual(processed, [
            statement({
                "type": TYPES["JSX_START_TAG"],
                "tag": "div",
                "self_closes": True,
                "attributes": [],
                "children": [],
            }, 0),
        ])
        
        tree = parse_statement("<div\n\tfoo=\"bar\"\n>\n</div>\n")
        processed = process_tree(tree)
        self.assertEqual(processed, [
            statement({
                "type": TYPES["JSX_START_TAG"],
                "tag": "div",
                "self_closes": False,
                "attributes": [
                    statement({
                        "type": TYPES["JSX_ATTRIBUTE"],
                        "name": "foo",
                        "right_hand": statement("\"bar\"", 0),
                    }, 0),
                ],
                "children": [],
            }, 0),
        ])
        
        tree = parse_statement("<input\n/>\n")
        processed = process_tree(tree)
        self.assertEqual(processed, [
            statement({
                "type": TYPES["JSX_START_TAG"],
                "tag": "input",
                "self_closes": True,
                "attributes": [],
                "children": [],
            }, 0),
        ])

        tree = parse_statement("<div>\n<span>foo</span>\n</div>\n")
        processed = process_tree(tree)
        self.assertEqual(processed, [
            statement({
                "type": TYPES["JSX_START_TAG"],
                "tag": "div",
                "self_closes": False,
                "attributes": [],
                "children": [statement({
                    "type": TYPES["JSX_START_TAG"],
                    "tag": "span",
                    "self_closes": False,
                    "attributes": [],
                    "children": [statement("\"foo\"", 0)],
                }, 0)],
            }, 0),
        ])
        
    def test_return(self):
        tree = parse_statement("function foo()\n\treturn bar\n")
        processed = process_tree(tree)
        self.assertEqual(processed, [
            statement({
                "type": TYPES["FUNCTION"],
                "params": [],
                "name": "foo",
                "nested": [
                    statement({
                        "type": TYPES["RETURN"],
                        "value": statement("bar", 0),
                    }, 4),
                ],
            }, 0),
        ])

    def test_value_manipulation(self):
        tree = parse_statement("bar + baz")
        processed = process_tree(tree)
        self.assertEqual(processed, [
            statement({
                "type": TYPES["VALUE_MANIPULATION"],
                "values": [
                    statement("bar", 0),
                    "+",
                    statement("baz", 0),
                ],
            }, 0),
        ])

        tree = parse_statement("bar    -    \"string\"")
        processed = process_tree(tree)
        self.assertEqual(processed, [
            statement({
                "type": TYPES["VALUE_MANIPULATION"],
                "values": [
                    statement("bar", 0),
                    "-",
                    statement("\"string\"", 0),
                ],
            }, 0),
        ])

        tree = parse_statement("bar + baz + 'foo'")
        processed = process_tree(tree)
        self.assertEqual(processed, [
            statement({
                "type": TYPES["VALUE_MANIPULATION"],
                "values": [
                    statement("bar", 0),
                    "+",
                    statement({
                        "type": TYPES["VALUE_MANIPULATION"],
                        "values": [
                            statement("baz", 0),
                            "+",
                            statement("\"foo\"", 0),
                        ]
                    }, 0),
                ],
            }, 0),
        ])

    def test_one_line_function(self):
        tree = parse_statement("foo = bar()")
        processed = process_tree(tree)
        self.assertEqual(processed, [
            statement({
                "type": TYPES["VARIABLE_ASSIGNMENT"],
                "name": "foo",
                "value": statement({
                    "type": TYPES["CALL_FUNC"],
                    "function": {
                        "type": TYPES['FUNCTION_NAME'],
                        "name": statement("bar", 0),
                    },
                    "parameters": {'type': 'types/function_params', 'params': []},
                }, 0),
            }, 0),
        ])
        
    def test_else(self):
        tree = parse_statement("if foo == true\n\tbar = foo\nelse\n\tfoo = bar\n")
        processed = process_tree(tree)
        self.assertEqual(processed, [
            statement({
                "type": TYPES["IF"],
                "condition": {
                    "type": TYPES["CONDITION"],
                    "right_hand": statement("true", 0),
                    "left_hand": statement("foo", 0),
                    "condition": "==",
                },
                "nested": [
                    statement({
                        "type": TYPES["VARIABLE_ASSIGNMENT"],
                        "name": "bar",
                        "value": statement("foo", 0),
                    }, 4),
                ],
            }, 0),
            statement({
                "type": TYPES["ELSE"],
                "nested": [
                    statement({
                        "type": TYPES["VARIABLE_ASSIGNMENT"],
                        "name": "foo",
                        "value": statement("bar", 0),
                    }, 4),
                ],
            }, 0),
        ])

    def test_map_one_line(self):
        tree = parse_statement("{}")
        processed = process_tree(tree)
        self.assertEqual(processed, [
            statement({
                "type": TYPES["MAP"],
                "children": [],
            }, 0),
        ])
        
    def test_boolean(self):
        tree = parse_statement("foo = false")
        processed = process_tree(tree)
        self.assertEqual(processed, [
            statement({
                "type": TYPES["VARIABLE_ASSIGNMENT"],
                "name": "foo",
                "value": statement("false", 0),
            }, 0),
        ])
        tree = parse_statement("foo = true")
        processed = process_tree(tree)
        self.assertEqual(processed, [
            statement({
                "type": TYPES["VARIABLE_ASSIGNMENT"],
                "name": "foo",
                "value": statement("true", 0),
            }, 0),
        ])
        
if __name__ == "__main__":
    unittest.main()