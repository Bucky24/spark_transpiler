import unittest

if 'unittest.util' in __import__('sys').modules:
    # Show full diff in self.assertEqual.
    __import__('sys').modules['unittest.util']._MAX_LENGTH = 999999999

from grammar import parse_statement
from transformer import process_tree, TYPES
from preprocessor import preprocess

def statement(data, spaces):
    return {
        "type": TYPES["STATEMENT"],
        "spaces": spaces,
        "statement": data,
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

if __name__ == "__main__":
    unittest.main()