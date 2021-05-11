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
        
    def test_for_as_array(self):
        tree = parse_statement("for foo as bar\n    baz = bar\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        self.assertEqual(result, "for (var bar of foo) {\n    var baz = bar;\n}\n");
        
    def test_for_as_object(self):
        tree = parse_statement("for foo as bar : baz\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        self.assertEqual(result, "for (var bar in foo) {\n    var baz = foo[bar];\n}\n");
        
    def test_for_normal(self):
        tree = parse_statement("for i=0;i<5;i++\n    foo = i\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        self.assertEqual(result, "for (var i = 0;i < 5;i++) {\n    var foo = i;\n}\n");

if __name__ == "__main__":
    unittest.main()