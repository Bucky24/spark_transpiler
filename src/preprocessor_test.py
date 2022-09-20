import unittest

from grammar import parse_statement
from transformer import process_tree
from preprocessor import preprocess

class TestPreprocessor(unittest.TestCase):
    def test_frontend_pragma(self):
        tree = parse_statement("#frontend\nfoo = 'abcd'")
        processed = process_tree(tree)
        preprocessed = preprocess(processed)

        print(preprocessed)

if __name__ == "__main__":
    unittest.main()