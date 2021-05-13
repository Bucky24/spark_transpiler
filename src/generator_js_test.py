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
        
    def test_while(self):
        tree = parse_statement("foo = 5\nwhile foo > bar\n    foo = bar\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        self.assertEqual(result, "var foo = 5;\nwhile (foo > bar) {\n    foo = bar;\n}\n");

    def test_function_definition(self):
        tree = parse_statement("function foo()\n    bar = baz\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        self.assertEqual(result, "function foo() {\n    var bar = baz;\n}\n");
        
        tree = parse_statement("function()\n    bar = baz\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        self.assertEqual(result, "function() {\n    var bar = baz;\n}\n");
        
        tree = parse_statement("function foo(bar, baz)\n    bar = baz\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        self.assertEqual(result, "function foo(bar, baz) {\n    var bar = baz;\n}\n");
        
    def test_function_call(self):
        tree = parse_statement("func(\n    foo\n    bar\n    baz\n)\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        self.assertEqual(result, "func(\n    foo,\n    bar,\n    baz,\n\n);\n");
        
    def test_function_call_in_assignment(self):
        tree = parse_statement("foo = func(\n    foo\n    bar\n    baz\n)\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        self.assertEqual(result, "var foo = func(\n    foo,\n    bar,\n    baz,\n\n);\n");
        
    def test_nested_function_call(self):
        tree = parse_statement("func(\n    foo(\n        bar\n    )\n    baz\n)\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        self.assertEqual(result, "func(\n    foo(\n        bar,\n    \n    ),\n    baz,\n\n);\n");
        
    def test_function_with_function_call(self):
        tree = parse_statement("function foo()\n    printt(\n    )\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        self.assertEqual(result, "function foo() {\n    printt(\n    \n    );\n}\n");

    def test_class_definition(self):
        tree = parse_statement("class Foo")
        processed = process_tree(tree)
        result = generate(processed, "js")
        self.assertEqual(result, "class Foo {\n}\n");
        
        tree = parse_statement("class Foo extends Bar")
        processed = process_tree(tree)
        result = generate(processed, "js")
        self.assertEqual(result, "class Foo extends Bar {\n}\n");
        
    def test_class_functions(self):
        tree = parse_statement("class Foo\n    function constructor(a, b, c)\n        printt(\n        )\n\n    function foo()\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        self.assertEqual(result, "class Foo {\n    constructor(a, b, c) {\n        printt(\n        \n        );\n    }\n    foo() {\n    }\n}\n");
        
    def test_new_instance(self):
        tree = parse_statement("class Foo\nbar = Foo(\n)\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        self.assertEqual(result, "class Foo {\n}\nvar bar = new Foo(\n\n);\n");
        
    def test_class_variables(self):
        tree = parse_statement("foo = bar.baz.biz")
        processed = process_tree(tree)
        result = generate(processed, "js")
        self.assertEqual(result, "var foo = bar.baz.biz;\n");
        
    def test_class_method_call(self):
        tree = parse_statement("foo = bar.baz(\n\n)\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        self.assertEqual(result, "var foo = bar.baz(\n\n);\n");
        
        tree = parse_statement("foo = bar.baz.biz.buzz(\n\n)\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        self.assertEqual(result, "var foo = bar.baz.biz.buzz(\n\n);\n");
        
    def test_imports(self):
        tree = parse_statement("print(\n    foo\n)\n")
        processed = process_tree(tree)
        result, imports = generate(processed, "js")
        self.assertEqual(result, "const {\n    print\n} = require(\"./stdlib_js_common.js\");\n\nprint(\n    foo,\n\n);\n");
        self.assertEqual(imports, [{
            "type": "stdlib",
            "lang": "js",
            "library": "common",
        }])

if __name__ == "__main__":
    unittest.main()