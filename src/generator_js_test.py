import unittest

from generator import generate
from grammar import parse_statement
from transformer import process_tree


class TestGeneratorJs(unittest.TestCase):
    def test_variables(self):
        tree = parse_statement("foo = 'abcd'\nbar = foo\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        self.assertEqual(result, "var foo = \"abcd\";\nvar bar = foo;\n");

        tree = parse_statement("foo = 5.45\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        self.assertEqual(result, "var foo = 5.45;\n");

        tree = parse_statement("foo = 5\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        self.assertEqual(result, "var foo = 5;\n");

        tree = parse_statement("foo = 5\nfoo = foo ++\n");
        processed = process_tree(tree)
        result = generate(processed, "js")
        self.assertEqual(result, "var foo = 5;\nfoo = foo++;\n");

    def test_conditionals(self):
        tree = parse_statement("foo = 10\nif foo == bar\n    foo = bar\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        self.assertEqual(result, "var foo = 10;\nif (foo == bar) {\n    foo = bar;\n}\n");

if __name__ == "__main__":
    unittest.main()