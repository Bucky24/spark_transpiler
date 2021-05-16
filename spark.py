import argparse
from os import path, mkdir
import sys
import subprocess
import time
import shutil

script_dir = path.dirname(path.realpath(__file__))


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
    
    code = result[0]
    imports = result[1]

    print("Done")
    sys.stdout.flush()
    time.sleep(0.01)

    outFiles = {}
    for platform in code:
        platform_code = code[platform]
        platform_imports = imports[platform]

        if platform_code == "":
            continue

        sys.stdout.write("Generating files for {}... ".format(platform))
        sys.stdout.flush()
        
        cacheDir = path.realpath(script_dir + "/cache")

        if not path.exists(cacheDir):
            mkdir(cacheDir)
            
        # copy over any required imports
        for importFile in platform_imports:
            libPath = path.realpath(script_dir + "/" + importFile["type"] + "/" + importFile["lang"] + "/" + importFile["library"] + "/" + importFile["library"] + "." + importFile["extension"])
            newLibFile = importFile["type"] + "_" + importFile["lang"] + "_" + importFile["library"] + "." + importFile["extension"]
            newLibPath = path.realpath(cacheDir + "/" + newLibFile)
            shutil.copyfile(libPath, newLibPath)
            
        outFile = path.realpath(cacheDir + "/output_{}.js".format(platform))
        handle = open(outFile, "w")
        handle.write(platform_code)
        print("Done")
        sys.stdout.flush()
        time.sleep(0.01)
        outFiles[platform] = outFile

    print(">>>{}".format(outFiles["backend"]))
