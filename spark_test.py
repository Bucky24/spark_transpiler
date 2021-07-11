import unittest
import spark

generate_frontend_framework = spark.generate_frontend_framework
generate_code_from_file = spark.generate_code_from_file
pre_check_includes = spark.pre_check_includes
flatten_import_data = spark.flatten_import_data
process_pragmas = spark.process_pragmas

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
    global file_writes, file_copies

    for mock in mocks:
        setattr(mock["inst"], mock["value"], mock["func"])
        
    del mocks[:]
    file_writes = {}
    file_copies = {}
    
def _return_false(*args):
    return False
    
def _return_true(*args):
    return True
    
def _mock_realpath(file_map):
    def _realpath(file):
        return file_map[file]
        
    _mock(spark, "_realpath", _realpath)
    
def _mock_readfile(file_map):
    def _file_contents(file):
        return file_map[file]

    _mock(spark, "_read_file", _file_contents)
    
file_writes = {};

def _mock_writefile():
    def _do_write_file(file, data):
        if file not in file_writes:
            file_writes[file] = []
        file_writes[file].append(data)
        
    _mock(spark, "_write_file", _do_write_file)
    
file_copies = {};

def _mock_copyfile():
    def _do_copy_file(from_path, to):
        file_copies[from_path] = to
    
    _mock(spark, "_copy_file", _do_copy_file)
    
def _mock_fileexists(fileList):
    def _do_fileexists(file):
        return file in fileList
        
    _mock(spark, "_file_exists", _do_fileexists)
        
def _mock_libraries():
    _mock_readfile({
        "webapp.tmpl.js": "const frontendFiles = {\n//<FRONTEND_IMPORTS>\n};\n//<BACKEND_IMPORTS>\n",
        "index.tmpl.html": "<!-- FRONTEND_SCRIPTS -->",
        "common_backend.js": "",
    })
    _mock_realpath({
        "script_path/stdlib/js/backend/webapp.tmpl.js": "webapp.tmpl.js",
        "cache_path/stdlib_js_backend_webapp.js": "cache_path/stdlib_js_backend_webapp.js",
        "script_path/stdlib/js/frontend/index.tmpl.html": "index.tmpl.html",
        "cache_path/stdlib_js_frontend_index.html": "cache_path/stdlib_js_frontend_index.html",
        "script_path/stdlib/js/backend/common.js": "common_backend.js",
        "cache_path/stdlib_js_backend_common.js": "cache_path/stdlib_js_backend_common.js",
        "cache_path/stdlib_js_frontend_common.js": "cache_path/stdlib_js_frontend_common.js",
    })
    
    def _override_script():
        return "script_path"

    _mock(spark, "_script_dir", _override_script)
    _mock_cachedir()
    
def _mock_cachedir():  
    def _override_cache(path):
        return "cache_path"

    _mock(spark, "_cache_dir", _override_cache)
        

class TestGenerateCode(unittest.TestCase):
    def tearDown(self):
        _clean_mocks()
        
    def test_failure_on_not_exist(self):
        _mock(spark, "_file_exists", _return_false)
        
        result = generate_code_from_file("test_file", "label", None)
        self.assertIsNone(result)
        
    def test_code_generation(self):
        _mock(spark, "_file_exists", _return_true)
        _mock_readfile({
            "/test_file": "print(\n    foo\n)"
        })
        _mock_realpath({
            "test_file": "/test_file",
        })

        output = generate_code_from_file("test_file", "label", None)
        code = output["code"]
        imports = output["internal_imports"]
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

class TestPreCheckIncludes(unittest.TestCase):
    def tearDown(self):
        _clean_mocks()

    def test_single_file_no_includes(self):
        _mock(spark, "_file_exists", _return_true)
        _mock_realpath({
            "foo.spark": "/foo.spark",
        })
        _mock_readfile({
            "/foo.spark": "",
        })
        
        # returns expected data for one file
        file = "foo.spark"
        result = pre_check_includes([file])
        
        self.assertEquals(result, {
            "file_import_data": {
                file: { "frontend": {}, "backend": {} },
            },
            "files_to_run": [file],
            "id_to_file_map": {
                "foo_out": file,
            },
            "file_ids": ["foo_out"],
            "file_to_id_map": {
                file: "foo_out",
            },
        })
        
    def test_single_file_with_includes(self):
        _mock(spark, "_file_exists", _return_true)
        _mock_realpath({
            "foo.spark": "/foo.spark",
            "bar.spark": "/bar.spark",
            "/bar.spark": "/bar.spark",
        })
        _mock_readfile({
            "/foo.spark": "#include bar.spark\n",
            "/bar.spark": ""
        })

        result = pre_check_includes(["foo.spark"])
        
        self.assertEquals(result, {
            "file_import_data": {
                "/bar.spark": { "frontend": {}, "backend": {} },
                "foo.spark": { "frontend": {}, "backend": {'/bar.spark': []} },
            },
            "files_to_run": ["foo.spark", "/bar.spark"],
            "id_to_file_map": {
                "foo_out": "foo.spark",
                "bar_out": "/bar.spark",
            },
            "file_ids": ["foo_out", "bar_out"],
            "file_to_id_map": {
                "/bar.spark": "bar_out",
                "foo.spark": "foo_out",
            },
        })
        
    def test_single_file_with_chain_includes(self):
        _mock(spark, "_file_exists", _return_true)
        _mock_realpath({
            "foo.spark": "/foo.spark",
            "bar.spark": "/bar.spark",
            "/bar.spark": "/bar.spark",
            "baz.spark": "/baz.spark",
            "/baz.spark": "/baz.spark",
        })
        _mock_readfile({
            "/foo.spark": "#include bar.spark\n",
            "/bar.spark": "#include baz.spark\n",
            "/baz.spark": "",
        })

        result = pre_check_includes(["foo.spark"])
        
        self.assertEquals(result, {
            "file_import_data": {
                "/bar.spark": { "frontend": {}, "backend": {'/baz.spark': [] } },
                "/baz.spark": { "frontend": {}, "backend": { } },
                "foo.spark": { "frontend": {}, "backend": {'/bar.spark': []} },
            },
            "files_to_run": ["foo.spark", "/bar.spark", "/baz.spark"],
            "id_to_file_map": {
                "foo_out": "foo.spark",
                "bar_out": "/bar.spark",
                "baz_out": "/baz.spark",
            },
            "file_ids": ["foo_out", "bar_out", "baz_out"],
            "file_to_id_map": {
                "/bar.spark": "bar_out",
                "/baz.spark": "baz_out",
                "foo.spark": "foo_out",
            },
        })
        
    def test_multiple_files_with_no_includes(self):
        _mock(spark, "_file_exists", _return_true)
        _mock_realpath({
            "foo.spark": "/foo.spark",
            "bar.spark": "/bar.spark",
        })
        _mock_readfile({
            "/foo.spark": "",
            "/bar.spark": "",
        })

        result = pre_check_includes(["foo.spark", "bar.spark"])
        
        self.assertEquals(result, {
            "file_import_data": {
                "bar.spark": { "frontend": {}, "backend": { } },
                "foo.spark": { "frontend": {}, "backend": { } },
            },
            "files_to_run": ["bar.spark", "foo.spark"],
            "id_to_file_map": {
                "foo_out": "foo.spark",
                "bar_out": "bar.spark",
            },
            "file_ids": ["bar_out", "foo_out"],
            "file_to_id_map": {
                "bar.spark": "bar_out",
                "foo.spark": "foo_out",
            },
        })
        
    def test_single_file_with_named_inputs(self):
        _mock(spark, "_file_exists", _return_true)
        _mock_realpath({
            "foo.spark": "/foo.spark",
            "bar.spark": "/bar.spark",
            "/bar.spark": "/bar.spark",
        })
        _mock_readfile({
            "/foo.spark": "#include baz from bar.spark",
            "/bar.spark": "",
        })

        result = pre_check_includes(["foo.spark"])
        
        self.assertEquals(result, {
            "file_import_data": {
                "/bar.spark": { "frontend": {}, "backend": {} },
                "foo.spark": { "frontend": {}, "backend": {'/bar.spark': ['baz']} },
            },
            "files_to_run": ["foo.spark", "/bar.spark"],
            "id_to_file_map": {
                "foo_out": "foo.spark",
                "bar_out": "/bar.spark",
            },
            "file_ids": ["foo_out", "bar_out"],
            "file_to_id_map": {
                "/bar.spark": "bar_out",
                "foo.spark": "foo_out",
            },
        })
        
    def test_frontend_imports(self):
        _mock(spark, "_file_exists", _return_true)
        _mock_realpath({
            "foo.spark": "/foo.spark",
            "bar.spark": "/bar.spark",
            "/bar.spark": "/bar.spark",
        })
        _mock_readfile({
            "/foo.spark": "#frontend\n#include baz from bar.spark",
            "/bar.spark": "",
        })

        result = pre_check_includes(["foo.spark"])
        
        self.assertEquals(result, {
            "file_import_data": {
                "/bar.spark": { "frontend": {}, "backend": {} },
                "foo.spark": { "frontend": {'/bar.spark': ['baz']}, "backend": {} },
            },
            "files_to_run": ["foo.spark", "/bar.spark"],
            "id_to_file_map": {
                "foo_out": "foo.spark",
                "bar_out": "/bar.spark",
            },
            "file_ids": ["foo_out", "bar_out"],
            "file_to_id_map": {
                "/bar.spark": "bar_out",
                "foo.spark": "foo_out",
            },
        })

class TestGenerateFrontendFramework(unittest.TestCase):
    def tearDown(self):
        _clean_mocks()

    def test_no_imports(self):
        _mock_writefile()
        _mock_copyfile()
        _mock_libraries()
        _mock_fileexists(['back1.js'])

        outfiles = {
            "frontend": ['front1.js'],
            "backend": [],
        }
        imports = []
        backend_file = "back1.js"
        
        generate_frontend_framework(outfiles, imports, backend_file, "base_dir")
        
        self.assertEquals(file_writes, {
            "cache_path/stdlib_js_backend_webapp.js": [
                "const frontendFiles = {\n\t\"front1.js\": \"front1.js\",\n};\nrequire(\"back1.js\");\n",
            ],
            "cache_path/stdlib_js_frontend_index.html": ["<script src=\"front1.js\" defer></script>"],
        })
        self.assertEquals(file_copies, {
            "common_backend.js": "cache_path/stdlib_js_backend_common.js",
        })
        self.assertEquals(outfiles["backend"], ['cache_path/stdlib_js_backend_webapp.js'])
        
    def test_with_imports(self):
        _mock_writefile()
        _mock_copyfile()
        _mock_libraries()
        _mock_fileexists(['back1.js'])

        outfiles = {
            "frontend": ['front1.js'],
            "backend": [],
        }
        imports = [
            {
                "type": "stdlib",
                "lang": "js",
                "library": "common",
                "extension": "js",
                "category": "frontend",
            }
        ]
        backend_file = "back1.js"
        
        generate_frontend_framework(outfiles, imports, backend_file, "dir")
        
        self.assertEquals(file_writes, {
            "cache_path/stdlib_js_backend_webapp.js": [
                "const frontendFiles = {\n\t\"stdlib_js_frontend_common.js\": \"cache_path/stdlib_js_frontend_common.js\",\n\t\"front1.js\": \"front1.js\",\n};\nrequire(\"back1.js\");\n",
            ],
            "cache_path/stdlib_js_frontend_index.html": ["<script src=\"stdlib_js_frontend_common.js\" defer></script>\n<script src=\"front1.js\" defer></script>"],
        })
        self.assertEquals(file_copies, {
            "common_backend.js": "cache_path/stdlib_js_backend_common.js",
        })
        self.assertEquals(outfiles["backend"], ['cache_path/stdlib_js_backend_webapp.js'])
        
    def test_no_backend_file(self):
        def test_no_imports(self):
            _mock_writefile()
            _mock_copyfile()
            _mock_libraries()

            outfiles = {
                "frontend": ['front1.js'],
                "backend": [],
            }
            imports = []
            backend_file = "back1.js"
        
            generate_frontend_framework(outfiles, imports, backend_file)
        
            self.assertEquals(file_writes, {
                "cache_path/stdlib_js_backend_webapp.js": [
                    "const frontendFiles = {\n\t\"front1.js\": \"front1.js\",\n};\n",
                ],
                "cache_path/stdlib_js_frontend_index.html": ["<script src=\"front1.js\" defer></script>"],
            })
            self.assertEquals(file_copies, {
                "common_backend.js": "cache_path/stdlib_js_backend_common.js",
            })
            self.assertEquals(outfiles["backend"], ['cache_path/stdlib_js_backend_webapp.js'])
        
class TestFlattenImportData(unittest.TestCase):
    def test_flatten_import_data(self):
        import_data = {
            "frontend": {
                "file1.spark": ["class1", "function1"],
            },
            "backend": {
                "file2.spark": ["class3", "function2"],
            },
        }
        
        file_classes = {
            "file1.spark": {
                "frontend": ["class1", "class2"],
            },
            "file2.spark": {
                "backend": ["class3", "class4"],
            },
        }
        
        result = flatten_import_data(import_data, file_classes)
        
        self.assertEquals(result, {
            "frontend": {
                "functions": [],
                "classes": ["class1"],
            },
            "backend": {
                "functions": [],
                "classes": ["class3"],
            },
        })
        
class TestProcessPragmas(unittest.TestCase):
    def tearDown(self):
        _clean_mocks()

    def test_frontend_with_no_includes(self):
        pragmas = []
        code = "code"
        file_to_id_map = {}
        base_dir = "base/"
        
        result = process_pragmas("file1.spark", "frontend", pragmas, code, file_to_id_map, base_dir)
        
        self.assertEqual(result['frontend_imports'], [])
        self.assertEqual(result['platform_code'], code)
        
    def test_backend_with_no_includes(self):
        pragmas = []
        code = "code"
        file_to_id_map = {}
        base_dir = "base/"
        
        result = process_pragmas("file1.spark", "backend", pragmas, code, file_to_id_map, base_dir)
        
        self.assertEqual(result['frontend_imports'], [])
        self.assertEqual(result['platform_code'], code)

    def test_frontend_with_just_file_include(self):
        _mock_realpath({
            "file1.spark": "/file1.spark",
            "//file2.spark": "/file2.spark",
        })
        pragmas = [{
            "type": "include",
            "value": "file2.spark",
        }]
        code = "code"
        file_to_id_map = {
            "/file2.spark": "file2",
        }
        base_dir = "base/"
        
        result = process_pragmas("file1.spark", "frontend", pragmas, code, file_to_id_map, base_dir)
        
        self.assertEqual(result['frontend_imports'], [
            "await Modules[\"file2\"];",
        ])
        self.assertEqual(result['platform_code'], code)
        
    def test_backend_with_just_file_include(self):
        _mock_realpath({
            "file1.spark": "/file1.spark",
            "//file2.spark": "/file2.spark",
            "cache_path/output_backend__file2.js": "cache_path/output_backend__file2.js",
        })
        _mock_cachedir()
        pragmas = [{
            "type": "include",
            "value": "file2.spark",
        }]
        code = "code"
        file_to_id_map = {
            "/file2.spark": "file2",
        }
        base_dir = "base/"
    
        result = process_pragmas("file1.spark", "backend", pragmas, code, file_to_id_map, base_dir)
    
        self.assertEqual(result['frontend_imports'], [])
        self.assertEqual(result['platform_code'], "require(\"cache_path/output_backend__file2.js\");\n" + code)
        
    def test_frontend_with_complex_include(self):
        _mock_realpath({
            "file1.spark": "/file1.spark",
            "//file2.spark": "/file2.spark",
        })
        pragmas = [{
            "type": "include",
            "value": "foo,bar from file2.spark",
        }]
        code = "code"
        file_to_id_map = {
            "/file2.spark": "file2",
        }
        base_dir = "base/"
    
        result = process_pragmas("file1.spark", "frontend", pragmas, code, file_to_id_map, base_dir)
    
        self.assertEqual(result['frontend_imports'], [
            "const {foo,bar} = await Modules[\"file2\"];",
        ])
        self.assertEqual(result['platform_code'], code)

    def test_backend_with_complex_include(self):
        _mock_realpath({
            "file1.spark": "/file1.spark",
            "//file2.spark": "/file2.spark",
            "cache_path/output_backend__file2.js": "cache_path/output_backend__file2.js",
        })
        _mock_cachedir()
        pragmas = [{
            "type": "include",
            "value": "foo,bar from file2.spark",
        }]
        code = "code"
        file_to_id_map = {
            "/file2.spark": "file2",
        }
        base_dir = "base/"
    
        result = process_pragmas("file1.spark", "backend", pragmas, code, file_to_id_map, base_dir)
    
        self.assertEqual(result['frontend_imports'], [])
        self.assertEqual(result['platform_code'], "const {foo,bar} = require(\"cache_path/output_backend__file2.js\");\n" + code)

if __name__ == "__main__":
    unittest.main()