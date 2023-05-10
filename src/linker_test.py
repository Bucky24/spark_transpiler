import unittest
from linker import link_code, generate_and_link_inner
from file import FileMock

if 'unittest.util' in __import__('sys').modules:
    # Show full diff in self.assertEqual.
    __import__('sys').modules['unittest.util']._MAX_LENGTH = 999999999

from grammar import parse_statement
from transformer import process_tree, TYPES
from preprocessor import preprocess
from utils import print_tree

class TestLinker(unittest.TestCase):
    def setUp(self):
        FileMock.reset()

    def test_code_linking(self):
        result = link_code("before <<<bar/foo>>> after <<<bar/foo>>>", [{
            "type": "internal",
            "link": "bar/foo"
        }], {
            "bar/foo": { "real_path": "./src/bar/foo.js" },
        }, "base")

        self.assertEqual(result,"before ./src/bar/foo.js after ./src/bar/foo.js")

    def test_backend_only(self):
        FileMock.abspath_set("./base", "/User/foo/base")
        FileMock.abspath_set("./build", "/User/bar/build")
        FileMock.abspath_set("./src/sample.spark", "/User/foo/base/src/sample.spark")
        FileMock.read_set("/User/foo/base/src/sample.spark", "#sample2\n#sample3\nfoo = bar")
        FileMock.read_set("/User/foo/base/src/sample2.spark", "bar = baz")
        FileMock.read_set("/User/foo/base/src/sample3.spark", "baz = bar")

        generate_and_link_inner(["src/sample.spark"], "./build", "./base", "js", FileMock)

        sampleContents = FileMock.get_write("/User/bar/build/src/sample.spark_backend.js")
        self.assertEqual(sampleContents, "(async () => {\n    const sample3 = require(\"./src/sample3.spark_backend.js\");\n\n    const sample2 = require(\"./src/sample2.spark_backend.js\");\n\n    let foo = bar;\n})();\n")

    def test_several_files(self):
        FileMock.abspath_set("./base", "/User/foo/base")
        FileMock.abspath_set("./build", "/User/bar/build")
        FileMock.abspath_set("./src/file1.spark", "/User/foo/base/src/file1.spark")
        FileMock.abspath_set("./src/file2.spark", "/User/foo/base/src/file2.spark")
        FileMock.read_set("/User/foo/base/src/file1.spark", "#file3\nfoo = bar")
        FileMock.read_set("/User/foo/base/src/file2.spark", "bar = baz")
        FileMock.read_set("/User/foo/base/src/file3.spark", "three = four")

        generate_and_link_inner(["/src/file1.spark", "/src/file2.spark"], "./build", "./base", "js", FileMock)

        sampleContents = FileMock.get_write("/User/bar/build/src/file1.spark_backend.js")
        self.assertEqual(sampleContents, "(async () => {\n    const file3 = require(\"./src/file3.spark_backend.js\");\n\n    let foo = bar;\n})();\n")
        sampleContents = FileMock.get_write("/User/bar/build/src/file2.spark_backend.js")
        self.assertEqual(sampleContents, "(async () => {\n    let bar = baz;\n})();\n")
        sampleContents = FileMock.get_write("/User/bar/build/src/file3.spark_backend.js")
        self.assertEqual(sampleContents, "(async () => {\n    let three = four;\n})();\n")

        dirs = FileMock.mkdir_get()
        self.assertEqual(dirs, ["/User/bar/build"])
    
    def test_import(self):
        FileMock.abspath_set("./base", "/User/foo/base")
        FileMock.abspath_set("./build", "/User/bar/build")
        FileMock.abspath_set("./src/file1.spark", "/User/foo/base/src/file1.spark")
        FileMock.read_set("/User/foo/base/src/file1.spark", "print(\n    \"foo\"\n)")

        generate_and_link_inner(["/src/file1.spark"], "./build", "./base", "js", FileMock)

        copys = FileMock.copy_get()
        self.assertEqual(len(copys), 1)
        self.assertIn('../stdlib/js/backend/common.js', copys[0]['from'])
        self.assertEqual(copys[0]['to'], '/User/bar/build/stdlib/common_js_backend.js')

if __name__ == "__main__":
    unittest.main()