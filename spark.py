import argparse
from os import path, mkdir, remove
import sys
import subprocess
import time
import shutil
import glob

script_dir = path.dirname(path.realpath(__file__))
cacheDir = path.realpath(script_dir + "/cache")

from src import generator, grammar, transformer
    
# These util methods split out so they can be stubbed in tests
def _read_file(file):
    handle = open(file)
    contents = handle.read()
    handle.close()
    return contents
    
def _write_file(file, contents):
    handle = open(file, "w")
    contents = handle.write(contents)
    handle.close()
    
def _copy_file(oldPath, newPath):
    shutil.copyfile(oldPath, newPath)
    
def _file_exists(file):
    return path.exists(file)
  
# Library helper files  
def _get_library(libType, lang, category, library, extension):
        libPath = path.realpath(script_dir + "/" + libType + "/" + lang + "/" + category + "/" + library + "." + extension)
        return _read_file(libPath)

def _get_new_lib_path(libType, lang, category, library, extension):
    newLibFile = libType + "_" + lang + "_" + category + "_" + library + "." + extension
    newLibPath = path.realpath(cacheDir + "/" + newLibFile)
    return newLibPath

def _write_library(libType, lang, category, library, extension, contents):
    newLibPath = _get_new_lib_path(libType, lang, category, library, extension)
    _write_file(newLibPath, contents)
    return newLibPath

def _copy_library(libType, lang, category, library, extension):
    libPath = path.realpath(script_dir + "/" + libType + "/" + lang + "/" + category + "/" + library + "." + extension)
    newLibPath = _get_new_lib_path(libType, lang, category, library, extension)
    _copy_file(libPath, newLibPath)
    
def generate_code_from_file(file):
    fullPath = path.realpath(file)
    if not _file_exists(fullPath):
        print("Cannot find input file {}".format(fullPath))
        return None
    
    sys.stdout.write("Reading... ")
    sys.stdout.flush()
    contents = _read_file(fullPath)
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
    result = generator.generate(processed, lang)

    code = result[0]
    imports = result[1]

    print("Done")
    sys.stdout.flush()
    time.sleep(0.01)

    return code, imports

def generate_frontend_framework(outFiles, imports):
    # if we have ANY frontend code, our backend needs to contain the initial setup code to display said frontend
    app_contents = _get_library(
        "stdlib",
        lang,
        "backend",
        "webapp",
        "tmpl.js",
    )

    frontend_imports = []

    # first, load up all the frontend imports. These should have already been copied over by the previous step
    for platform_import in imports["frontend"]:
        lib_path = _get_new_lib_path(
            platform_import["type"],
            platform_import["lang"],
            platform_import["category"],
            platform_import["library"],
            platform_import["extension"],
        )
        frontend_imports.append(lib_path)

    frontend_imports.append(outFiles["frontend"])

    frontend_import_code_list = []
    for import_file in frontend_imports:
        filename = path.basename(import_file)
        frontend_import_code_list.append("\t\"{}\": \"{}\",".format(filename, import_file.replace("\\", "\\\\")))

    frontend_import_string = "\n".join(frontend_import_code_list)

    # now load up all the backend files and generate the import list
    backend_import_list = []
    #for file in outFiles["backend"]:
    # right now it's just one file
    backend_import_list.append("require(\"{}\");".format(outFiles["backend"]))

    backend_import_string = "\n".join(backend_import_list)

    final_content = app_contents.replace("//<FRONTEND_IMPORTS>", frontend_import_string)
    final_content = final_content.replace("//<BACKEND_IMPORTS>", backend_import_string)
    file_path = _write_library(
        "stdlib",
        lang,
        "backend",
        "webapp",
        "js",
        final_content,
    )
    outFiles["backend"] = file_path

    # then we need to generate the frontend index template

    index_contents = _get_library(
        "stdlib",
        lang,
        "frontend",
        "index",
        "tmpl.html",
    )

    scripts = []

    for import_file in frontend_imports:
        filename = path.basename(import_file)
        scripts.append("<script src=\"" + filename + "\"></script>")

    final_index_content = index_contents.replace("<!-- FRONTEND_SCRIPTS -->", format("\n".join(scripts)))
    _write_library(
        "stdlib",
        lang,
        "frontend",
        "index",
        "html",
        final_index_content,
    )

lang = "js"

def main():
    parser = argparse.ArgumentParser(description='Spark CLI')
    parser.add_argument('files', metavar='File', type=str, nargs='+', help='A file to process')

    args = parser.parse_args()

    if not _file_exists(cacheDir):
        mkdir(cacheDir)

    files = glob.glob(path.realpath(cacheDir + "/*"))
    for f in files:
        remove(f)

    # right now we're assuming we only have 1 file
    for file in args.files:
        result = generate_code_from_file(file)
        
        if not result:
            sys.exit(1)
            
        code, imports = result

        outFiles = {}
        for platform in code:
            platform_code = code[platform]
            platform_imports = imports[platform]

            if platform_code == "":
                continue

            sys.stdout.write("Generating files for {}... ".format(platform))
            sys.stdout.flush()

            # copy over any required imports
            for importFile in platform_imports:
                _copy_library(
                    importFile["type"],
                    importFile["lang"],
                    importFile["category"],
                    importFile["library"],
                    importFile["extension"],
                )

            outFile = path.realpath(cacheDir + "/output_{}.js".format(platform))
            handle = open(outFile, "w")
            handle.write(platform_code)
            print("Done")
            sys.stdout.flush()
            time.sleep(0.01)
            outFiles[platform] = outFile

        # this all needs to be moved to a utility method so we can unit test it
        if outFiles.get("frontend", None):
            sys.stdout.write("Generating frontend framework... ")
            sys.stdout.flush()
            time.sleep(0.01)
        
            generate_frontend_framework(outFiles, imports)
        
            print("Done")
            sys.stdout.flush()
            time.sleep(0.01)

        print(">>>{}".format(outFiles["backend"]))

if __name__ == "__main__":
    main()
