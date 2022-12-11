import os
import sys
import time

# neccessary on windows so that generator can find generator_js when called from spark.py
# for whatever reason
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

import grammar 
from transformer import process_tree
from preprocessor import preprocess
from generator_js import generate_js#, generate_external_exports


_COMMON_CODE = {
    "}": [grammar.Tree('map_end', [])],
    ")": [grammar.Tree('end_call_function', [])],
    "{": [grammar.Tree('map_start', [])],
}

def generate(transformed, lang, label="label"):
    if lang == "js":
        frontend_result = generate_js(
            transformed['frontend'],
            transformed["frontend_function_imports"],
            transformed['frontend_class_imports'],
            transformed['custom_imports_frontend'],
            label,
            "frontend",
        )
        backend_result = generate_js(
            transformed['backend'],
            transformed["backend_function_imports"],
            transformed['backend_class_imports'],
            transformed['custom_imports_backend'],
            label,
            "backend",
        )

        result = {
            "code": {
                "frontend": frontend_result["code"],
                "backend": backend_result["code"],
            },
            "imports": {
                "frontend": frontend_result["imports"],
                "backend": backend_result["imports"],
            },
            "classes": {
                "frontend": frontend_result["classes"],
                "backend": backend_result["classes"],
            }
        }
        return result

def generate_from_code(code, lang, label):
    tree = grammar.parse_statement(code)
    processed = process_tree(tree)
    preprocessed = preprocess(processed)

    return generate(preprocessed, lang, label)