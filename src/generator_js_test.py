import unittest

from generator import generate
from grammar import parse_statement
from transformer import process_tree


def _wrap_front(code):
    return "(async () => {\n" + code + "\n})();\n"

class TestGeneratorJs(unittest.TestCase):
    def test_variables(self):
        tree = parse_statement("foo = 'abcd'\nbar = foo\n")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "var foo = \"abcd\";\nvar bar = foo;\n");

        tree = parse_statement("foo = 5.45\n")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "var foo = 5.45;\n");

        tree = parse_statement("foo = 5\n")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "var foo = 5;\n");

        tree = parse_statement("foo = 5\nfoo = foo ++\n");
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "var foo = 5;\nfoo = foo++;\n");

    def test_conditionals(self):
        tree = parse_statement("foo = 10\nif foo == bar\n    foo = bar\n")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "var foo = 10;\nif (foo == bar) {\n    foo = bar;\n}\n");
        
    def test_for_as_array(self):
        tree = parse_statement("for foo as bar\n    baz = bar\n")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "for (var bar of foo) {\n    var baz = bar;\n}\n");
        
    def test_for_as_object(self):
        tree = parse_statement("for foo as bar : baz\n")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "for (var bar in foo) {\n    var baz = foo[bar];\n}\n");
        
    def test_for_normal(self):
        tree = parse_statement("for i=0;i<5;i++\n    foo = i\n")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "for (var i = 0;i < 5;i++) {\n    var foo = i;\n}\n");
        
    def test_while(self):
        tree = parse_statement("foo = 5\nwhile foo > bar\n    foo = bar\n")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "var foo = 5;\nwhile (foo > bar) {\n    foo = bar;\n}\n");

    def test_function_definition(self):
        tree = parse_statement("function foo()\n    bar = baz\n")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "function foo() {\n    var bar = baz;\n}\n");
        
        tree = parse_statement("function()\n    bar = baz\n")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "function() {\n    var bar = baz;\n}\n");
        
        tree = parse_statement("function foo(bar, baz)\n    bar = baz\n")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "function foo(bar, baz) {\n    var bar = baz;\n}\n");
        
    def test_function_call(self):
        tree = parse_statement("func(\n    foo\n    bar\n    baz\n)\n")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "func(\n    foo,\n    bar,\n    baz,\n\n);\n");
        
    def test_function_call_in_assignment(self):
        tree = parse_statement("foo = func(\n    foo\n    bar\n    baz\n)\n")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "var foo = func(\n    foo,\n    bar,\n    baz,\n\n);\n");
        
    def test_nested_function_call(self):
        tree = parse_statement("func(\n    foo(\n        bar\n    )\n    baz\n)\n")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "func(\n    foo(\n        bar,\n    \n    ),\n    baz,\n\n);\n");
        
    def test_function_with_function_call(self):
        tree = parse_statement("function foo()\n    printt(\n    )\n")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "function foo() {\n    printt(\n    \n    );\n}\n");

    def test_class_definition(self):
        tree = parse_statement("class Foo")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "class Foo {\n}\n");
        
        tree = parse_statement("class Foo extends Bar")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "class Foo extends Bar {\n}\n");
        
    def test_class_functions(self):
        tree = parse_statement("class Foo\n    function constructor(a, b, c)\n        printt(\n        )\n\n    function foo()\n")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "class Foo {\n    constructor(a, b, c) {\n        printt(\n        \n        );\n    }\n    foo() {\n    }\n}\n");
        
    def test_new_instance(self):
        tree = parse_statement("class Foo\nbar = Foo(\n)\n")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "class Foo {\n}\nvar bar = new Foo(\n\n);\n");
        
    def test_class_variables(self):
        tree = parse_statement("foo = bar.baz.biz")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "var foo = bar.baz.biz;\n");
        
    def test_class_method_call(self):
        tree = parse_statement("foo = bar.baz(\n\n)\n")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "var foo = bar.baz(\n\n);\n");
        
        tree = parse_statement("foo = bar.baz.biz.buzz(\n\n)\n")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "var foo = bar.baz.biz.buzz(\n\n);\n");
        
    def test_imports(self):
        tree = parse_statement("print(\n    foo\n)\n")
        processed = process_tree(tree)
        result, imports = generate(processed, "js")
        self.assertEqual(result["backend"], "const {\n    print\n} = require(\"./stdlib_js_backend_common.js\");\n\nprint(\n    foo,\n\n);\n");
        self.assertEqual(imports["backend"], [{
            "extension": "js",
            "type": "stdlib",
            "lang": "js",
            "library": "common",
            "category": "backend",
        }])

    def test_platforms_and_imports(self):
        tree = parse_statement("#frontend\nprint(\n    foo\n)\n#backend\nprint(\n    foo\n)\n")
        processed = process_tree(tree)
        result, imports = generate(processed, "js")
        self.assertEqual(result["backend"], "const {\n    print\n} = require(\"./stdlib_js_backend_common.js\");\n\nprint(\n    foo,\n\n);\n");
        self.assertEqual(imports["backend"], [{
            "category": "backend",
            "extension": "js",
            "type": "stdlib",
            "lang": "js",
            "library": "common",
        }])
        self.assertEqual(result["frontend"], _wrap_front("await print(\n    foo,\n\n);\n"));
        self.assertEqual(imports["frontend"], [{
            "extension": "js",
            "type": "stdlib",
            "lang": "js",
            "library": "common",
            "category": "frontend",
        }])

    def test_platform_unwind_blocks(self):
        tree = parse_statement("if foo == bar\n    if bar == baz\n        baz(\n            bin\n        )\n#frontend\nfoo = bar\n")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "if (foo == bar) {\n    if (bar == baz) {\n        baz(\n            bin,\n        \n        );\n    }\n}\n")
        self.assertEqual(result["frontend"], _wrap_front("var foo = bar;\n"))
        
    def test_platform_class_imports(self):
        tree = parse_statement("#frontend\nfoo = Component(\n\t\"div\"\n)\n")
        processed = process_tree(tree)
        result, imports = generate(processed, "js")
        self.assertEqual(result["frontend"], _wrap_front("var foo = new Component(\n    \"div\",\n\n);\n"))
        self.assertEqual(imports["frontend"], [
            {
                "lang": "js",
                "category": "frontend",
                "type": "stdlib",
                "extension": "js",
                "library": "frontend",
            },
        ])
    
    def test_arrays(self):
        tree = parse_statement("foo = [\n\t'bar'\n\t'baz'\n]\n")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "var foo = [\n    \"bar\",\n    \"baz\",\n\n];\n")
        
    def test_maps(self):
        tree = parse_statement("foo = {\n\tabcd: 'foo'\n}\n")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "var foo = {\n    \"abcd\": \"foo\",\n\n};\n")
        
    def test_nested_map_array(self):
        tree = parse_statement("foo = {\n\t[\n\t\t{\n\t\t\tfoo: 'bar'\n\t\t}\n\t]\n}\n")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "var foo = {\n    [\n        {\n            \"foo\": \"bar\",\n        \n        },\n    \n    ],\n\n};\n")
        
    def test_function_call_with_maps_and_arrays(self):
        tree = parse_statement("foo(\n\t{\n\t\tbar: baz\n\t}\n\t[\n\t\tbaz\n\t]\n)\n")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "foo(\n    {\n        \"bar\": baz,\n    \n    },\n    [\n        baz,\n    \n    ],\n\n);\n")
        
    def test_jsx(self):
        expected_imports = [{
            "category": "frontend",
            "extension": "js",
            "lang": "js",
            "library": "frontend",
            "type": "stdlib",
        }]
        tree = parse_statement("#frontend\n<div>\n</div>\n")
        processed = process_tree(tree)
        result, imports = generate(processed, "js")
        self.assertEqual(result["frontend"], _wrap_front("new Component(\"div\", {}, [\n\n]);\n"))  
        self.assertEqual(imports["frontend"], expected_imports)
        
        tree = parse_statement("#frontend\n<div/>\n")
        processed = process_tree(tree)
        result, imports = generate(processed, "js")
        self.assertEqual(result["frontend"], _wrap_front("new Component(\"div\", {}, []);\n"))
        self.assertEqual(imports["frontend"], expected_imports)
        
        tree = parse_statement("#frontend\n<div\n\tfoo=\"bar\"\n>\n</div>\n")
        processed = process_tree(tree)
        result, imports = generate(processed, "js")
        self.assertEqual(result["frontend"], _wrap_front("new Component(\"div\", {\n    foo: \"bar\",\n\n}, [\n\n]);\n"))
        self.assertEqual(imports["frontend"], expected_imports)
        
    def test_jsx_component(self):
        tree = parse_statement("#frontend\nclass Foo extends Component\n<Foo>\n</Foo>\n")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["frontend"], _wrap_front("class Foo extends Component {\n}\nnew Foo({}, [\n\n]);\n"))
        
    def test_return(self):
        tree = parse_statement("function foo()\n\treturn bar\n")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "function foo() {\n    return bar;\n}\n")
        
        tree = parse_statement("#frontend\nfunction foo()\n\treturn <div\n\t\tstyle=style\n\t>\n\t</div>\n")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["frontend"], _wrap_front("async function foo() {\n    return new Component(\"div\", {\n        style: style,\n    \n    }, [\n    \n    ]);\n}\n"))
        
    def test_multiple_block_closures(self):
        tree = parse_statement("class Foo\n\tfunction bar()\n\t\tif foo == bar\n\t\t\tfoo = bar\n\nfoo(\n\tfoo\n)\n")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "class Foo {\n    bar() {\n        if (foo == bar) {\n            var foo = bar;\n        }\n    }\n}\nfoo(\n    foo,\n\n);\n")

    def test_value_manipulation(self):
        tree = parse_statement("bar + baz")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "bar + baz;\n")

        tree = parse_statement("bar    -    \"string\"")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "bar - \"string\";\n")

        tree = parse_statement("bar + baz + 'foo'")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "bar + baz + \"foo\";\n")

    def test_value_manipulation_with_function(self):
        tree = parse_statement("bar + foo(\n\tbaz\n)\n")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "bar + foo(\n    baz,\n\n);\n")

    def test_one_line_function(self):
        tree = parse_statement("foo = bar()")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "var foo = bar();\n")

    def test_imports_with_chain(self):
        tree = parse_statement("Api.post()")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "const {\n    Api\n} = require(\"./stdlib_js_backend_common.js\");\n\nApi.post();\n")

    def test_function_call_and_platform(self):
        tree = parse_statement("foo()\n#frontend\nfoo()\n")
        processed = process_tree(tree)
        result, _ = generate(processed, "js")
        self.assertEqual(result["backend"], "foo();\n")
        self.assertEqual(result["frontend"], _wrap_front("await foo();\n"))

if __name__ == "__main__":
    unittest.main()