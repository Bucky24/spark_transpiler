import os
import sys
import time

# neccessary on windows so that generator can find generator_js when called from spark.py
# for whatever reason
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

import grammar 
from transformer import process_tree
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
            }
        }
        return result

def generate_from_code(code, lang, label, import_data):
    lines = code.split("\n")

    # So what are we doing here?
    # Lark apparently has a hard time with whitespace. Like a really hard time.
    # But only when generating the parse tree. So this code gathers info on the spaces,
    # generates the parse tree per line with no whitespace, and then adds them back
    # in manually. This takes a 16 second compile down to 2.5. For some reason.
    statements = []
    for line in lines:
        spaces = []
        for char in line:
            if char == " ":
                spaces.append(grammar.Token("SPACE", " "))
            elif char == "\t":
                spaces.append(grammar.Token("TAB", "\t"))
            else:
                break

        line_no_space = line.strip()

        if line_no_space == '':
            continue
        statement = _COMMON_CODE.get(line_no_space, None)
        if statement is None:
            start = time.time()
            tree = grammar.parse_statement(line_no_space + "\n")
            end = time.time()
            
            statement = tree.children[0].children[0]
            #print(line_no_space, (end - start))
        else:
            # we may manipulate the statement further on with spaces, so we need to make sure children
            # is a clean copy
            statement = grammar.Tree('statement', [] + statement)

        if isinstance(statement, grammar.Tree) and spaces:
            spaces.reverse()
            for space in spaces:
                statement.children.insert(0, grammar.Tree("spaces", [space]))
        statements.append(statement)
        
    tree = grammar.Tree("start", [
        grammar.Tree("statements", statements)
    ])
    processed = process_tree(tree)

    return generate(processed, lang, label, import_data)