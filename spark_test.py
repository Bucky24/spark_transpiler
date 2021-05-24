import unittest
import spark

generate_frontend_framework = spark.generate_frontend_framework
generate_code_from_file = spark.generate_code_from_file

mocks = []
def _mock(inst, value, newFn):
    oldFn = getattr(inst, value)
    setattr(inst, value, newFn)
    mocks.append({
        "inst": inst,
        "value": value,
        "func": oldFn,
    })
    return oldFn
    
def _clean_mocks():
    for mock in mocks:
        setattr(mock["inst"], mock["value"], mock["func"])
        
    del mocks[:]
    
def _return_false(*args):
    return False
    
def _return_true(*args):
    return True

class TestGenerateCode(unittest.TestCase):
    def tearDown(self):
        _clean_mocks()
        
    def test_failure_on_not_exist(self):
        _mock(spark, "_file_exists", _return_false)
        
        result = generate_code_from_file("test_file")
        self.assertIsNone(result)
        
    def test_code_generation(self):
        _mock(spark, "_file_exists", _return_true)
        
        code = "print(\n    foo\n)"
        
        def _file_contents(*args):
            return code
            
        _mock(spark, "_read_file", _file_contents)
        
        code, imports = generate_code_from_file("test_file")
        self.assertEqual(code["frontend"], "")
        self.assertEqual(code["backend"], "const {\n    print\n} = require(\"./stdlib_js_backend_common.js\");\n\nprint(\n    foo,\n\n);\n")
        self.assertEqual(imports["frontend"], [])
        self.assertEqual(imports["backend"], [{
            "lang": "js",
            "extension": "js",
            "category": "backend",
            "library": "common",
            "type": "stdlib",
        }])

if __name__ == "__main__":
    unittest.main()