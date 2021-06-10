import unittest

from generator import generate_from_code

class TestGenerator(unittest.TestCase):
    def test_code(self):
        result = generate_from_code("function foo()\n\tbar()\n", "js", "label", None)
        result = result[0]
        self.assertEqual(result["backend"], "function foo() {\n    bar();\n}\n\nmodule.exports = {\n\tfoo\n};\n")
        
if __name__ == "__main__":
    unittest.main()