import unittest

if 'unittest.util' in __import__('sys').modules:
    # Show full diff in self.assertEqual.
    __import__('sys').modules['unittest.util']._MAX_LENGTH = 999999999

from generator import generate, process_external_exports
from grammar import parse_statement
from transformer import process_tree


def _wrap_front(code, imports = None, label = "label"):
    if imports is None:
        return "Modules[\"" + label + "\"] = (async () => {\nawait new Promise((resolve) => {setTimeout(resolve, 10);});\n//<IMPORTS>\n" + code + "\n})();\n"
        
def _wrap_back(code):
    return "(async () => {\n" + code + "\n})();\n"

class TestGeneratorJs(unittest.TestCase):
    def test_variables(self):
        tree = parse_statement("foo = 'abcd'\nbar = foo\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("var foo = \"abcd\";\nvar bar = foo;\n"))

        tree = parse_statement("foo = 5.45\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("var foo = 5.45;\n"))

        tree = parse_statement("foo = 5\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("var foo = 5;\n"))

        tree = parse_statement("foo = 5\nfoo = foo ++\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("var foo = 5;\nfoo = foo++;\n"))
        
    def test_conditionals(self):
        tree = parse_statement("foo = 10\nif foo == bar\n    foo = bar\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("var foo = 10;\nif (foo == bar) {\n    foo = bar;\n}\n"))
        
    def test_for_as_array(self):
        tree = parse_statement("for foo as bar\n    baz = bar\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("for (var bar of foo) {\n    var baz = bar;\n}\n"))
        
    def test_for_as_object(self):
        tree = parse_statement("for foo as bar : baz\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("for (var bar in foo) {\n    var baz = foo[bar];\n}\n"))
        
    def test_for_normal(self):
        tree = parse_statement("for i=0;i<5;i++\n    foo = i\n")
        processed = process_tree(tree)
        result= generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("for (var i = 0;i < 5;i++) {\n    var foo = i;\n}\n"))
        
    def test_while(self):
        tree = parse_statement("foo = 5\nwhile foo > bar\n    foo = bar\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("var foo = 5;\nwhile (foo > bar) {\n    foo = bar;\n}\n"))

    def test_function_definition(self):
        tree = parse_statement("function foo()\n    bar = baz\n")
        processed = process_tree(tree)
        result= generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("async function foo() {\n    var bar = baz;\n}\n\nmodule.exports = {\n\tfoo\n};\n"))
        
        tree = parse_statement("function()\n    bar = baz\n")
        processed = process_tree(tree)
        result= generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("async () => {\n    var bar = baz;\n}\n"))
        
        tree = parse_statement("function foo(bar, baz)\n    bar = baz\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("async function foo(bar, baz) {\n    var bar = baz;\n}\n\nmodule.exports = {\n\tfoo\n};\n"))
        
    def test_function_call(self):
        tree = parse_statement("func(\n    foo\n    bar\n    baz\n)\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("await func(\n    foo,\n    bar,\n    baz,\n\n);\n"))
        
    def test_function_call_in_assignment(self):
        tree = parse_statement("foo = func(\n    foo\n    bar\n    baz\n)\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("var foo = await func(\n    foo,\n    bar,\n    baz,\n\n);\n"))
        
    def test_nested_function_call(self):
        tree = parse_statement("func(\n    foo(\n        bar\n    )\n    baz\n)\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("await func(\n    await foo(\n        bar,\n    \n    ),\n    baz,\n\n);\n"))
        
    def test_function_with_function_call(self):
        tree = parse_statement("function foo()\n    printt(\n    )\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("async function foo() {\n    await printt(\n    \n    );\n}\n\nmodule.exports = {\n\tfoo\n};\n"))

    def test_class_definition(self):
        tree = parse_statement("class Foo")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("class Foo {\n}\n\nmodule.exports = {\n\tFoo\n};\n"))
        
        tree = parse_statement("class Foo extends Bar")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("class Foo extends Bar {\n}\n\nmodule.exports = {\n\tFoo\n};\n"))
        
    def test_class_functions(self):
        tree = parse_statement("class Foo\n    function constructor(a, b, c)\n        printt(\n        )\n\n    function foo()\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("class Foo {\n    constructor(a, b, c) {\n        printt(\n        \n        );\n    }\n    async foo() {\n    }\n}\n\nmodule.exports = {\n\tFoo\n};\n"))
        
    def test_new_instance(self):
        tree = parse_statement("class Foo\nbar = Foo(\n)\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("class Foo {\n}\nvar bar = new Foo(\n\n);\n\nmodule.exports = {\n\tFoo\n};\n"))
        
    def test_class_variables(self):
        tree = parse_statement("foo = bar.baz.biz")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("var foo = bar.baz.biz;\n"))
        
    def test_class_method_call(self):
        tree = parse_statement("foo = bar.baz(\n\n)\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("var foo = await bar.baz(\n\n);\n"))
        
        tree = parse_statement("foo = bar.baz.biz.buzz(\n\n)\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("var foo = await bar.baz.biz.buzz(\n\n);\n"))
        
    def test_imports(self):
        tree = parse_statement("print(\n    foo\n)\n")
        processed = process_tree(tree)
        output = generate(processed, "js")
        result = output["code"]
        imports = output["internal_imports"]
        self.assertEqual(result["backend"], _wrap_back("const {\n    print\n} = require(\"./stdlib_js_backend_common.js\");\n\nawait print(\n    foo,\n\n);\n"))
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
        output = generate(processed, "js")
        result = output["code"]
        imports = output["internal_imports"]
        self.assertEqual(result["backend"], _wrap_back("const {\n    print\n} = require(\"./stdlib_js_backend_common.js\");\n\nawait print(\n    foo,\n\n);\n"))
        self.assertEqual(imports["backend"], [{
            "category": "backend",
            "extension": "js",
            "type": "stdlib",
            "lang": "js",
            "library": "common",
        }])
        self.assertEqual(result["frontend"], _wrap_front("await print(\n    foo,\n\n);\n"))
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
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("if (foo == bar) {\n    if (bar == baz) {\n        await baz(\n            bin,\n        \n        );\n    }\n}\n"))
        self.assertEqual(result["frontend"], _wrap_front("var foo = bar;\n"))
        
    def test_platform_class_imports(self):
        tree = parse_statement("#frontend\nfoo = Component(\n\t\"div\"\n)\n")
        processed = process_tree(tree)
        output = generate(processed, "js")
        result = output["code"]
        imports = output["internal_imports"]
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
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("var foo = [\n    \"bar\",\n    \"baz\",\n\n];\n"))
        
    def test_maps(self):
        tree = parse_statement("foo = {\n\tabcd: 'foo'\n}\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("var foo = {\n    \"abcd\": \"foo\",\n\n};\n"))
        
    def test_nested_map_array(self):
        tree = parse_statement("foo = {\n\t[\n\t\t{\n\t\t\tfoo: 'bar'\n\t\t}\n\t]\n}\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("var foo = {\n    [\n        {\n            \"foo\": \"bar\",\n        \n        },\n    \n    ],\n\n};\n"))
        
    def test_function_call_with_maps_and_arrays(self):
        tree = parse_statement("foo(\n\t{\n\t\tbar: baz\n\t}\n\t[\n\t\tbaz\n\t]\n)\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("await foo(\n    {\n        \"bar\": baz,\n    \n    },\n    [\n        baz,\n    \n    ],\n\n);\n"))
        
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
        output = generate(processed, "js")
        result = output["code"]
        imports = output["internal_imports"]
        self.assertEqual(result["frontend"], _wrap_front("new Component(\"div\", {}, [\n\n]);\n"))  
        self.assertEqual(imports["frontend"], expected_imports)
        
        tree = parse_statement("#frontend\n<div/>\n")
        processed = process_tree(tree)
        output = generate(processed, "js")
        result = output["code"]
        imports = output["internal_imports"]
        self.assertEqual(result["frontend"], _wrap_front("new Component(\"div\", {}, []);\n"))
        self.assertEqual(imports["frontend"], expected_imports)
        
        tree = parse_statement("#frontend\n<div\n\tfoo=\"bar\"\n>\n</div>\n")
        processed = process_tree(tree)
        output = generate(processed, "js")
        result = output["code"]
        imports = output["internal_imports"]
        self.assertEqual(result["frontend"], _wrap_front("new Component(\"div\", {\n    foo: \"bar\",\n\n}, [\n\n]);\n"))
        self.assertEqual(imports["frontend"], expected_imports)
        
        tree = parse_statement("#frontend\n<input\n/>\n")
        processed = process_tree(tree)
        output = generate(processed, "js")
        result = output["code"]
        imports = output["internal_imports"]
        self.assertEqual(result["frontend"], _wrap_front("new Component(\"input\", {\n\n}, []);\n"))
        self.assertEqual(imports["frontend"], expected_imports)
        
    def test_jsx_component(self):
        tree = parse_statement("#frontend\nclass Foo extends Component\n<Foo>\n</Foo>\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["frontend"], _wrap_front("class Foo extends Component {\n}\nnew Foo({}, [\n\n]);\n\nreturn {\n\tFoo\n};\n"))
        
    def test_return(self):
        tree = parse_statement("function foo()\n\treturn bar\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("async function foo() {\n    return bar;\n}\n\nmodule.exports = {\n\tfoo\n};\n"))
        
        tree = parse_statement("#frontend\nfunction foo()\n\treturn <div\n\t\tstyle={style}\n\t>\n\t</div>\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["frontend"], _wrap_front("async function foo() {\n    return new Component(\"div\", {\n        style: style,\n    }, [\n    \n    ]);\n}\n\nreturn {\n\tfoo\n};\n"))
        
    def test_multiple_block_closures(self):
        tree = parse_statement("class Foo\n\tfunction bar()\n\t\tif foo == bar\n\t\t\tfoo = bar\n\nfoo(\n\tfoo\n)\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("class Foo {\n    async bar() {\n        if (foo == bar) {\n            var foo = bar;\n        }\n    }\n}\nawait foo(\n    foo,\n\n);\n\nmodule.exports = {\n\tFoo\n};\n"))

    def test_value_manipulation(self):
        tree = parse_statement("bar + baz")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("bar + baz;\n"))

        tree = parse_statement("bar    -    \"string\"")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("bar - \"string\";\n"))

        tree = parse_statement("bar + baz + 'foo'")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("bar + baz + \"foo\";\n"))

    def test_value_manipulation_with_function(self):
        tree = parse_statement("bar + foo(\n\tbaz\n)\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("bar + await foo(\n    baz,\n);\n"))

    def test_one_line_function(self):
        tree = parse_statement("foo = bar()")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("var foo = await bar();\n"))

    def test_imports_with_chain(self):
        tree = parse_statement("Api.post()")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("const {\n    Api\n} = require(\"./stdlib_js_backend_common.js\");\n\nawait Api.post();\n"))

    def test_function_call_and_platform(self):
        tree = parse_statement("foo()\n#frontend\nfoo()\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("await foo();\n"))
        self.assertEqual(result["frontend"], _wrap_front("await foo();\n"))
      
    def test_else(self):
        tree = parse_statement("if foo == true\nelse\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("if (foo == true) {\n}\nelse {\n}\n"))
        
    def test_pragma(self):
        tree = parse_statement("#foo bar\n")
        processed = process_tree(tree)
        output = generate(processed, "js")
        result = output["code"]
        pragmas = output["pragmas"]
        self.assertEqual(pragmas["backend"], [
            {
                "type": "foo",
                "value": "bar",
            },
        ])
        tree = parse_statement("#foo\n")
        processed = process_tree(tree)
        output = generate(processed, "js")
        result = output["code"]
        pragmas = output["pragmas"]
        self.assertEqual(pragmas["backend"], [
            {
                "type": "foo",
            },
        ])

    def test_map_one_line(self):
        tree = parse_statement("{}")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("{};\n"))

    def test_export_functions_classes_backend(self):
        tree = parse_statement("function foo()\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("async function foo() {\n}\n\nmodule.exports = {\n\tfoo\n};\n"))

        tree = parse_statement("function()")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("async () => {\n}\n"))

        tree = parse_statement("class Foo\n\tfunction bar()\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("class Foo {\n    async bar() {\n    }\n}\n\nmodule.exports = {\n\tFoo\n};\n"))

        tree = parse_statement("class Foo\nfunction bar()\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        code = result["code"]
        classes = result["classes"]
        self.assertEqual(code["backend"], _wrap_back("class Foo {\n}\nasync function bar() {\n}\n\nmodule.exports = {\n\tbar,\n\tFoo\n};\n"))
        self.assertEqual(classes["backend"], ["Foo"])

    def test_export_functions_classes_frontend(self):
        tree = parse_statement("#frontend\nfunction foo()\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["frontend"], _wrap_front("async function foo() {\n}\n\nreturn {\n\tfoo\n};\n"))

        tree = parse_statement("#frontend\nfunction()\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["frontend"], _wrap_front("async () => {\n}\n"))

        tree = parse_statement("#frontend\nclass Foo\n\tfunction bar()\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["frontend"], _wrap_front("class Foo {\n    async bar() {\n    }\n}\n\nreturn {\n\tFoo\n};\n"))

        tree = parse_statement("#frontend\nclass Foo\nfunction bar()\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        code = result["code"]
        classes = result["classes"]
        self.assertEqual(code["frontend"], _wrap_front("class Foo {\n}\nasync function bar() {\n}\n\nreturn {\n\tbar,\n\tFoo\n};\n"))
        self.assertEqual(classes["frontend"], ["Foo"])

    def test_labels(self):
        tree = parse_statement("#frontend\nfoo = bar\n")
        processed = process_tree(tree)
        result = generate(processed, "js", "frontend_label")
        result = result["code"]
        self.assertTrue(result["frontend"].startswith("Modules[\"frontend_label\"] = (async ()"))

    def test_imports_backend(self):
        tree = parse_statement("foo = Bar()\n")
        processed = process_tree(tree)
        result = generate(processed, "js", None, {"backend": {"classes": ["Bar"]}})
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("var foo = new Bar();\n"))

    def test_imports_frontend(self):
        tree = parse_statement("#frontend\nfoo = Bar()\n")
        processed = process_tree(tree)
        result = generate(processed, "js", None, {"frontend": {"classes": ["Bar"]}})
        result = result["code"]
        self.assertEqual(result["frontend"], _wrap_front("var foo = new Bar();\n"))
        
    def test_boolean(self):
        tree = parse_statement("foo = false")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("var foo = false;\n"))
        
        tree = parse_statement("foo = true")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("var foo = true;\n"))

    def test_variable_chain(self):
        tree = parse_statement("this.foo.bar = baz")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("this.foo.bar = baz;\n"))

    def test_method_call_in_constructor(self):
        tree = parse_statement("#frontend\nclass Foo\n\tfunction constructor()\n\t\tbar()\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["frontend"], _wrap_front("class Foo {\n    constructor() {\n        bar();\n    }\n}\n\nreturn {\n\tFoo\n};\n"))

    def test_function_in_jsx_map_array(self):
        tree = parse_statement("#frontend\n<input\n\tonChange=function(event)\n\t\tfoo()\n\tvalue=\"bar\"\n/>\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["frontend"], _wrap_front("new Component(\"input\", {\n    onChange: async (event) => {\n        await foo();\n    },\n    value: \"bar\",\n\n}, []);\n"))

        tree = parse_statement("foo = {\n\tonChange: function(event)\n\t\tfoo()\n\tvalue: \"bar\"\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("var foo = {\n    \"onChange\": async (event) => {\n        await foo();\n    },\n    \"value\": \"bar\",\n}\n"))

        tree = parse_statement("foo = [\n\tfunction(event)\n\t\tfoo()\n\t\"bar\"\n]\n")
        processed = process_tree(tree)
        result = generate(processed, "js")
        result = result["code"]
        self.assertEqual(result["backend"], _wrap_back("var foo = [\n    async (event) => {\n        await foo();\n    },\n    \"bar\",\n\n];\n"))
        
    def test_mysql(self):
        tree = parse_statement("table = Table(\n\t\"table1\"\n\t[\n\t]\n\tTable.SOURCE_MYSQL\n)\n")
        processed = process_tree(tree)
        output = generate(processed, "js")
        imports = output['external_imports']
        self.assertEqual(imports, [{"module": "mysql", "version": "2.18.1"}])
        
        tree = parse_statement("table = Table(\n\t\"table1\"\n\t[\n\t]\n\tTable.SOURCE_FILE\n)\n")
        processed = process_tree(tree)
        output = generate(processed, "js")
        imports = output['external_imports']
        self.assertEqual(imports, [])

class TestGenerateExternalExports(unittest.TestCase):
    def test_no_exports(self):
        result = process_external_exports("js", [])
        json = result["data"]
        file = result["file"]
        command = result["command"]

        self.assertEqual(json, "{\n    \"dependencies\": {}\n}")
        self.assertEqual(file, "package.json")
        self.assertEqual(command, "npm install")

    def test_with_exports(self):
        result = process_external_exports("js", [
            {
                "module": "test",
                "version": "1.0.0",
            },
            {
                "module": "test2",
                "version": "0.2.0",
            }
        ])
        json = result["data"]

        self.assertEqual(json, "{\n    \"dependencies\": {\n        \"test\": \"1.0.0\", \n        \"test2\": \"0.2.0\"\n    }\n}")

if __name__ == "__main__":
    unittest.main()