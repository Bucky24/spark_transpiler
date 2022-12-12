import unittest
from linker import link_code

if 'unittest.util' in __import__('sys').modules:
    # Show full diff in self.assertEqual.
    __import__('sys').modules['unittest.util']._MAX_LENGTH = 999999999

from grammar import parse_statement
from transformer import process_tree, TYPES
from preprocessor import preprocess
from utils import print_tree

class TestLinker(unittest.TestCase):
    def test_code_linking(self):
        result = link_code("before <<<bar/foo>>> after <<<bar/foo>>>", ["bar/foo"], {
            "bar/foo": "./src/bar/foo.js",
        })

        self.assertEqual(result,"before ./src/bar/foo.js after ./src/bar/foo.js")

if __name__ == "__main__":
    unittest.main()