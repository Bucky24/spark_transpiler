import argparse
from os import path, mkdir, remove, getcwd, chdir
import sys
import subprocess
import time
import shutil
import glob
import threading
import json
import traceback

from src import generator, linker
"""
# These util methods split out so they can be stubbed in tests
def _script_dir():
    return path.dirname(path.realpath(__file__))
    
def _cache_dir(base_dir):
    return path.realpath(base_dir + "/sparkCache")

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
    
def _realpath(file):
    return path.realpath(file)
    
def _basename(file):
    return path.basename(file)
  
# Library helper files  
def _get_library(libType, lang, category, library, extension):
        libPath = _realpath(_script_dir() + "/" + libType + "/" + lang + "/" + category + "/" + library + "." + extension)
        return _read_file(libPath)

def _get_new_lib_path(libType, lang, category, library, extension, base_dir):
    newLibFile = libType + "_" + lang + "_" + category + "_" + library + "." + extension
    newLibPath = _realpath(_cache_dir(base_dir) + "/" + newLibFile)
    return newLibPath

def _write_library(libType, lang, category, library, extension, contents, base_dir):
    newLibPath = _get_new_lib_path(libType, lang, category, library, extension, base_dir)
    _write_file(newLibPath, contents)
    return newLibPath

def _copy_library(libType, lang, category, library, extension, base_dir):
    libPath = _realpath(_script_dir() + "/" + libType + "/" + lang + "/" + category + "/" + library + "." + extension)
    newLibPath = _get_new_lib_path(libType, lang, category, library, extension, base_dir)
    _copy_file(libPath, newLibPath)
    
# end util methods

def generate_code_from_file(file, label, import_data):
    fullPath = _realpath(file)
    if not _file_exists(fullPath):
        print("Cannot find input file {}".format(fullPath))
        return None

    fileBase = _basename(fullPath)
    print("Compiling {}...".format(fileBase))
    sys.stdout.flush()
    time.sleep(0.01)

    sys.stdout.write("Reading... ")
    sys.stdout.flush()
    contents = _read_file(fullPath)
    print("Done")
    sys.stdout.flush()
    time.sleep(0.01)
    
    sys.stdout.write("Generating code... ")
    sys.stdout.flush()
    time.sleep(0.01)
    contents += "\n"
    start = time.time()
    
    try:
        result = generator.generate_from_code(contents, lang, label, import_data)
    except Exception as err:
        exc_info = sys.exc_info()
        traceback.print_exception(*exc_info)
        del exc_info

    result_done = time.time()
    print("Done (total time {})".format(result_done - start))
    sys.stdout.flush()
    time.sleep(0.01)

    return result

def generate_frontend_framework(outFiles, imports, main_backend_file, base_dir):
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
    for platform_import in imports:
        lib_path = _get_new_lib_path(
            platform_import["type"],
            platform_import["lang"],
            platform_import["category"],
            platform_import["library"],
            platform_import["extension"],
            base_dir,
        )
        frontend_imports.append(lib_path)

    frontend_imports += outFiles["frontend"]

    frontend_import_code_list = []
    for import_file in frontend_imports:
        filename = path.basename(import_file)
        frontend_import_code_list.append("\t\"{}\": \"{}\",".format(filename, import_file.replace("\\", "\\\\")))

    frontend_import_string = "\n".join(frontend_import_code_list)

    # now load up all the backend files and generate the import list
    backend_import_list = []
    # we only need the main backend output, all others are imported from there.
    # it may not exist if the main file given has only frontend code. In that case just skip it
    if _file_exists(main_backend_file):
        backend_import_list.append("require(\"{}\");".format(main_backend_file.replace("\\", "\\\\")))
    

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
        base_dir,
    )
    outFiles["backend"] = [file_path]

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
        scripts.append("<script src=\"" + filename + "\" defer></script>")

    final_index_content = index_contents.replace("<!-- FRONTEND_SCRIPTS -->", format("\n".join(scripts)))
    _write_library(
        "stdlib",
        lang,
        "frontend",
        "index",
        "html",
        final_index_content,
        base_dir,
    )
    
    # we also will need the backend common lib because the backend system requires Api
    _copy_library(
        "stdlib",
        lang,
        "backend",
        "common",
        "js",
        base_dir,
    )

def get_cache_path(file, platform, base_dir):
    file_path = file.replace("../", "")
    file_path = file.replace("..\\", "")
    if base_dir[-1] == "/" or base_dir[-1] == "\\":
        file_path = file.replace(base_dir, "")
    else:
        file_path = file.replace(base_dir + "/", "")
        file_path = file.replace(base_dir + "\\", "")

    file_path = file_path.replace("./", "")
    file_path = file_path.replace(".\\", "")
    file_path = file_path.replace(".spark", "")
    file_path = file_path.replace("/", "_")
    # this needs to be more flexible
    file_path = file_path.replace("C:\\", "")
    file_path = file_path.replace("\\", "_")
    extension = ".js"
    _, file_ext = path.splitext(file_path)
    if file_ext:
        extension = ""
    outFile = _realpath(_cache_dir(base_dir) + "/output_{}_{}{}".format(platform, file_path, extension))
    outFile = outFile.replace("\\", "\\\\")
    return outFile

lang = "js"

def pre_check_includes(files):
    # pre-check all the files to deal with pre-processor statements
    id_to_file_map = {}
    files_to_run = []
    file_ids = []
    file_to_id_map = {}
    file_import_data = {}
    while len(files) > 0:
        file = files.pop()
        fullPath = _realpath(file)
        if not _file_exists(fullPath):
            print("Cannot find input file {}".format(fullPath))
            return None
        contents = _read_file(fullPath)
        lines = contents.split("\n")
        file_import_data[file] = {
            "frontend": {},
            "backend": {},
        }
        cur_platform = "backend"
        for line in lines:
            if line.startswith("#include"):
                line = line.replace("#include ", "")
                line_list = line.split(" ")
                included_file = line_list[0]
                includes = []
                if len(line_list) == 3:
                    included_file = line_list[2]
                    includes = line_list[0].split(",")
                #print(included_file)
                dirname = path.dirname(fullPath)
                if dirname[-1] != "/":
                    dirname += "/"
                    
                if dirname == "/":
                    dirname = ""
                new_path = _realpath(dirname + included_file)

                if included_file:
                    file_import_data[file][cur_platform][new_path] = includes
                files.append(new_path)
            if line == "#backend":
                cur_platform = "backend"
            elif line == "#frontend":
                cur_platform = "frontend"
        base = path.basename(file)
        file_list = base.split(".")
        file_name = file_list[0]
        cur_name = file_name
        counter = 1
        while cur_name in file_ids:
            cur_name = file_name + "_" + counter
            counter += 1
        cur_name += "_out"
        #print(cur_name, file)
        id_to_file_map[cur_name] = file
        file_to_id_map[file] = cur_name
        file_ids.append(cur_name)
        files_to_run.append(file)

    return {
        "id_to_file_map": id_to_file_map,
        "file_to_id_map": file_to_id_map,
        "file_ids": file_ids,
        "files_to_run": files_to_run,
        "file_import_data": file_import_data,
    }
  
# this method computes all the classes being imported into the file. This is useful because we
# need to know in code generation if something is a class or not, and this helps us know what
# classes we imported (since we wouldn't know they're a class any other way). Currently we are
# not making use of the functions field.
def flatten_import_data(import_data, file_classes):
    # flatten the import data by platform
    flattened_import_data = {
        "frontend": {
            "classes": [],
            "functions": [],
        },
        "backend": {
            "classes": [],
            "functions": [],
        },
    }

    for platform in import_data:
        import_files = import_data[platform]
        #print(import_files)
        for import_file in import_files:
            classes_in_file = file_classes.get(import_file, {}).get(platform, [])
            import_values = import_files[import_file]
            #print(import_file, import_values, classes_in_file)
            for value in import_values:
                if value in classes_in_file:
                    flattened_import_data[platform]["classes"].append(value)
    #print(flattened_import_data)
    
    return flattened_import_data
    
def process_pragmas(file, platform, platform_pragmas, platform_code, file_to_id_map, base_dir):
    fullFilePath = _realpath(file)
    frontend_imports = []
    # handle any included files
    for pragma in platform_pragmas:
        if pragma["type"] == "include":
            value = pragma["value"]
            value_list = value.split(" ")
            fullPath = None
            import_list = None
            if len(value_list) == 1:
                fullPath = _realpath(path.dirname(fullFilePath) + "/" + value)
            else:
                fullPath = _realpath(path.dirname(fullFilePath) + "/" + value_list[2])
                #files_to_run.append(fullPath)
                import_list = value_list[0]

            if fullPath:
                # this is technically a no-no because we are hard-coding our lang to JS right now by sending js code here
                if platform == "backend":
                    export_file = get_cache_path(fullPath, platform, base_dir)
                    import_code = "require(\"" + export_file + "\");\n"
                    if import_list:
                        import_code = "const {" + import_list + "} = require(\"" + export_file + "\");\n"
                    platform_code = import_code + platform_code
                elif platform == "frontend":
                    export_name = file_to_id_map[fullPath]
                    if import_list:
                        import_code = "const {" + import_list + "} = await Modules[\"" + export_name + "\"];"
                        frontend_imports.append(import_code)
                    else:
                        # in this case we have nothing to import, but we still want to wait until the promise of the import has
                        # resolved
                        import_code = "await Modules[\"" + export_name + "\"];"
                        frontend_imports.append(import_code)
                        
    return {
        "platform_code": platform_code,
        "frontend_imports": frontend_imports,
    }

def build_external_exports(lang, external_exports, base_dir):
    result = generator.process_external_exports(lang, external_exports)

    data = result["data"]
    file = result["file"]
    command = result["command"]

    cache_file = _realpath(_cache_dir(base_dir) + "/" + file)
    _write_file(cache_file, data)

    cwd = getcwd()
    chdir(_cache_dir(base_dir))
    child = subprocess.Popen(command, stdout=sys.stdout, stderr=sys.stderr, shell=True)
    child.communicate()
    chdir(cwd)
    if child.returncode != 0:
        raise Exception("Unable to build external exports")

def main():
    parser = argparse.ArgumentParser(description='Spark CLI')
    parser.add_argument('--single_file', dest='single_file', action='store_true', help='If set, this only compiles the one file and does nothing else')
    parser.add_argument('--base_directory', dest='base_dir', action='store', help='The base directory of the project')
    parser.add_argument('files', metavar='File', type=str, nargs='+', help='Files to process')
    parser.set_defaults(single_file=False)

    args = parser.parse_args()

    base_dir = args.base_dir        
    single_file = args.single_file
    files = [] + args.files
    
    process_files(base_dir, single_file, files)
    
def process_files(base_dir, single_file, files):
    cacheDir = _cache_dir(base_dir)
    
    if not _file_exists(cacheDir):
        mkdir(cacheDir)
        
    # not super ideal
    starting_file = files[0]
    
    if not single_file:
        cache_files = glob.glob(_realpath(cacheDir + "/*"))
        for f in cache_files:
            base = _basename(f)
            if base == "node_modules" or base == "package-lock.json":
                continue
            if path.isdir(f):
                shutil.rmtree(cacheDir)
            else:
                remove(f)

    # pre-check all the files to deal with pre-processor statements
    includes_result = pre_check_includes(files)
    id_to_file_map = includes_result["id_to_file_map"]
    file_ids = includes_result["file_ids"]
    files_to_run = includes_result["files_to_run"]
    file_to_id_map = includes_result["file_to_id_map"]
    file_import_data = includes_result["file_import_data"]

    outFiles = {
        "frontend": [],
        "backend": [],
    }

    file_classes = {}

    all_frontend_imports = []
    all_files_ran_over = []
    all_external_modules = []

    while len(files_to_run) > 0:
        file = files_to_run.pop()
        file_id = file_to_id_map[file]
        all_files_ran_over.append(file)

        if not file.endswith(".spark"):
            # in this case it's not code, copy it over without transforming
            outputFile = get_cache_path(file, "backend", base_dir)
            fileBase = _basename(file)
            outputBase = _basename(outputFile)

            sys.stdout.write("Copying {} to {}... ".format(fileBase, outputBase))
            sys.stdout.flush()
            contents = _read_file(file)
            _write_file(outputFile, contents)
            print("Done")
            sys.stdout.flush()
            time.sleep(0.01)
            continue

        import_data = file_import_data[file]

        #print(import_data)

        # flatten the import data by platform
        flattened_import_data = flatten_import_data(import_data, file_classes)
        
        result = None
        try:
            result = generate_code_from_file(file, file_id, flattened_import_data)
        except Exception as error:
            print(error)
            sys.stderr.write("FAILURE\n")
        
        if not result:
            sys.exit(1)
            
        code = result['code']
        imports = result['internal_imports']
        pragmas = result['pragmas']
        classes = result['classes']
        external_imports = result['external_imports']

        file_classes[file] = classes
        all_external_modules += external_imports

        for platform in code:
            platform_code = code[platform]
            #print(imports, platform)
            platform_imports = imports[platform]
            platform_pragmas = pragmas[platform]

            if platform == "frontend":
                for imp in platform_imports:
                    # dumb, like really dumb, but eh. Need some sort of an id to do it more efficiently
                    found = False
                    for imp2 in all_frontend_imports:
                        if (
                            imp["type"] == imp2["type"] and
                            imp["lang"] == imp2["lang"] and
                            imp["category"] == imp2["category"] and
                            imp["library"] == imp2["library"] and
                            imp["extension"] == imp2["extension"]
                        ):
                            found = True
                            break

                    if not found:
                        all_frontend_imports.append(imp)

            if platform_code == "" and not platform_pragmas:
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
                    base_dir,
                )
            
            result = process_pragmas(file, platform, platform_pragmas, platform_code, file_to_id_map, base_dir)
            frontend_imports = result['frontend_imports']
            platform_code = result['platform_code']

            if frontend_imports:
                platform_code = platform_code.replace("//<IMPORTS>", "\n".join(frontend_imports))

            outFile = get_cache_path(file, platform, base_dir)
            handle = open(outFile, "w")
            handle.write(platform_code)
            handle.close()
            print("Done")
            sys.stdout.flush()
            time.sleep(0.01)   
            outFiles[platform].insert(0, outFile)

    # this all needs to be moved to a utility method so we can unit test it
    if len(outFiles["frontend"]) > 0 and not single_file:
        sys.stdout.write("Generating frontend framework... ")
        sys.stdout.flush()
        time.sleep(0.01)
    
        main_backend_file = get_cache_path(starting_file, "backend", base_dir)
        generate_frontend_framework(outFiles, all_frontend_imports, main_backend_file, base_dir)
    
        print("Done")
        sys.stdout.flush()
        time.sleep(0.01)
        
    # build external modules
    build_external_exports("js", all_external_modules, base_dir)

    # write the last time of compile to the cache file
    updateFile = path.join(cacheDir, "__update_time__")
    handle = open(updateFile, "w")
    intTime = int(time.time())
    handle.write("{}".format(intTime))
    handle.close()

    result = {
        "all_files": all_files_ran_over,
    }
    if not single_file:
        result = {
            "outFile": outFiles["backend"][0],
            "all_files": all_files_ran_over,
        }

    print(">>>{}".format(json.dumps(result)))
    sys.stdout.flush()
    time.sleep(0.01)
"""



def main():
    parser = argparse.ArgumentParser(description='Spark CLI')
    parser.add_argument('--base_directory', dest='base_dir', action='store', help='The base directory of the project')
    parser.add_argument('--build_directory', dest='build_dir', action='store', help='The build directory of the project')
    parser.add_argument('files', metavar='File', type=str, nargs='+', help='Files to process')
    parser.add_argument('--lang', dest='lang', action='store', help='The language to transpile to')
    parser.set_defaults(single_file=False)

    args = parser.parse_args()

    base_dir = args.base_dir        
    files = [] + args.files
    build_dir = args.build_dir
    lang = args.lang

    linker.generate_and_link(files, build_dir, base_dir, lang)

    pass

if __name__ == "__main__":
    main()
