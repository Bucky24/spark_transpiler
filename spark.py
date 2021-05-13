import argparse
from os import path
import sys

from src import generator, grammar, transformer

parser = argparse.ArgumentParser(description='Spark CLI')
parser.add_argument('files', metavar='File', type=str, nargs='+', help='A file to process')

args = parser.parse_args()

for file in args.files:
    fullPath = path.realpath(file)
    if not path.exists(fullPath):
        print("Cannot find input file {}".format(fullPath))
        sys.exit(1)
        
    handle = open(fullPath)
    contents = handle.read()
    handle.close()
    print(contents)
    
    # the grammar requires a newline at the end of the file
    if contents[-1] != "\n":
        contents += "\n"
    
    tree = grammar.parse_statement(contents)
    processed = transformer.process_tree(tree)
    result = generator.generate(processed, "js")
    
    print(result)