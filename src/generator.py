import os
import sys

# neccessary on windows so that generator can find generator_js when called from spark.py
# for whatever reason
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

import grammar 
from transformer import process_tree
from generator_js import generate_js

def generate(transformed, lang):
    if lang == "js":
        return generate_js(transformed)

def generate_from_code(code, lang):
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

        tree = grammar.parse_statement(line.strip() + "\n")
        statement = tree.children[0].children[0]
        if isinstance(statement, grammar.Tree) and spaces:
            spaces.reverse()
            for space in spaces:
                statement.children.insert(0, grammar.Tree("spaces", [space]))
        statements.append(statement)
        
    tree = grammar.Tree("start", [
        grammar.Tree("statements", statements)
    ])
    processed = process_tree(tree)
    return generate(processed, lang)
