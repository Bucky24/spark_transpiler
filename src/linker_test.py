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
        result = link_code("before <<<bar/foo>>> after <<<bar/foo>>>", ["bar/foo"], {
            "bar/foo": "./src/bar/foo.js",
        })

        self.assertEqual(result,"before ./src/bar/foo.js after ./src/bar/foo.js")

    def test_backend_only(self):
        FileMock.abspath_set("./base", "/User/foo/base")
        FileMock.abspath_set("./build", "/User/bar/build")
        FileMock.abspath_set("./src/sample.spark", "/User/foo/base/src/sample.spark")
        FileMock.read_set("/User/foo/base/src/sample.spark", "#sample2\n#sample3\nfoo = bar")
        FileMock.read_set("/User/foo/base/src/sample2.spark", "bar = baz")
        FileMock.read_set("/User/foo/base/src/sample3.spark", "baz = bar")

        generate_and_link_inner(["./src/sample.spark"], "./build", "./base", "js", FileMock)

        sampleContents = FileMock.get_write("/User/bar/build/src/sample.spark_backend.js")
        self.assertEqual(sampleContents, "(async () => {\n    const sample3 = require(\"./src/sample3.spark_backend.js\");\n\n    const sample2 = require(\"./src/sample2.spark_backend.js\");\n\n    let foo = bar;\n})();\n")

    def test_several_files(self):
        generate_and_link_inner(["./src/file1.spark", "./src/file2.spark"], "./build", "./base", "js", FileMock)

if __name__ == "__main__":
    unittest.main()