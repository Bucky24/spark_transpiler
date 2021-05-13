import argparse
from os import path, mkdir
import sys
import subprocess
import time

from src import generator, grammar, transformer

parser = argparse.ArgumentParser(description='Spark CLI')
parser.add_argument('files', metavar='File', type=str, nargs='+', help='A file to process')

args = parser.parse_args()

for file in args.files:
    fullPath = path.realpath(file)
    if not path.exists(fullPath):
        print("Cannot find input file {}".format(fullPath))
        sys.exit(1)
        
    sys.stdout.write("Reading... ")
    sys.stdout.flush()
    handle = open(fullPath)
    contents = handle.read()
    handle.close()
    #print(contents)
    print("Done")
    sys.stdout.flush()
    time.sleep(0.01)

    sys.stdout.write("Generating code... ")
    sys.stdout.flush()
    
    # the grammar requires a newline at the end of the file
    if contents[-1] != "\n":
        contents += "\n"
    
    tree = grammar.parse_statement(contents)
    processed = transformer.process_tree(tree)
    result = generator.generate(processed, "js")
    print("Done")
    sys.stdout.flush()
    time.sleep(0.01)
    sys.stdout.write("Generating files... ")
    sys.stdout.flush()
    
    cacheDir = path.realpath("./cache")

    if not path.exists(cacheDir):
        mkdir(cacheDir)

    outFile = path.realpath(cacheDir + "/output.js")
    handle = open(outFile, "w")
    handle.write(result)
    print("Done")
    sys.stdout.flush()
    time.sleep(0.01)
    print(">>>{}".format(outFile))
