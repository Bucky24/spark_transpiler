import unittest

from generator import generate_from_code

class TestGenerator(unittest.TestCase):
    def test_code(self):
        result = generate_from_code("function foo()\n\tbar()\n", "js", "label")
        result = result["code"]
        self.assertEqual(result["backend"], "(async () => {\n    async function foo() {\n        await bar();\n    }\n\n    module.exports = {\n        foo\n    };\n\n})();\n")
        
if __name__ == "__main__":
    unittest.main()