import json

from file import File
from grammar import parse_statement
from transformer import process_tree
from preprocessor import preprocess
from generator import generate

# turn to true for debug logs
LOG = False

CURRENT_DIRECTORY = File.dirname(__file__)

def log(str):
    if LOG:
        print(str)

def link_code(code, be_imports, files_by_id, base_directory):
    for path in be_imports:
        if path['type'] == "internal":
            if path['link'] not in files_by_id:
                raise Exception("Import {} not found in files list!".format(path['link']))
            real_file_path = files_by_id[path['link']]["real_path"]
            relative_path = real_file_path.replace(base_directory, ".")
            code = code.replace("<<<{}>>>".format(path['link']), relative_path)

    return code

def generate_and_link(starting_files, build_directory, base_directory, lang):
    return generate_and_link_inner(starting_files, build_directory, base_directory,lang, File)

_FILE_ENDINGS = {
    "js": "js"
}

def generate_and_link_inner(starting_files, build_directory, base_directory, lang, files):
    queue = []
    files_by_id = {}
    id_by_file = {}
    file_id_base = 0

    def _get_id_for_file(file):
        nonlocal file_id_base

        if file not in id_by_file:
            new_id = "FILE:{}".format(file_id_base)
            file_id_base += 1
            files_by_id[new_id] = {
                "file": file,
            }
            id_by_file[file] = new_id

        return id_by_file[file]

    full_base_directory = files.abspath(base_directory)
    full_build_directory = files.abspath(build_directory)

    if not files.exists(full_build_directory):
        files.mkdir(full_build_directory)
    for file in starting_files:
        if file[0] != "/":
            file = "/" + file
        full_file = files.abspath(full_base_directory + file)
        relative_file = full_file.replace(full_base_directory, "")
        queue.insert(0, relative_file)

    be_map = {}
    fe_map = {}

    while len(queue) > 0:
        file = queue.pop()
        full_file = full_base_directory + file

        log("Processing " + full_file)

        file_directory = files.dirname(full_file)

        file_id = _get_id_for_file(full_file)

        file_data = files_by_id[file_id]

        contents = files.read(full_file)

        tree = parse_statement(contents)
        processed = process_tree(tree)
        preprocessed = preprocess(processed)
        result = generate(preprocessed, lang)
                
        backend_file = full_build_directory + file + "_backend." + _FILE_ENDINGS[lang]
        backend_code = result['code']['backend'] if result['code']['backend'] is not None else ""
        be_map[backend_file] = {
            "code": backend_code,
            "imports": result['imports']['backend'],
        }

        file_data['real_path'] = backend_file

        frontend_file = full_build_directory + file + "_frontend." + _FILE_ENDINGS[lang]
        frontend_code = result['code']['frontend'] if result['code']['frontend'] is not None else ""
        fe_map[frontend_file] = {
            "code": frontend_code,
            "imports": result['imports']['frontend'],
        }

        for item in result['imports']['backend']:
            if item['type'] == "internal":
                item_path = item['path']
                if item_path[0] != "/":
                    item_path = "/" + item_path
                proper_path = files.abspath(file_directory + item_path)
                import_id = _get_id_for_file(proper_path)
                be_map[backend_file]["code"] = be_map[backend_file]["code"].replace(item['link'], import_id)
                item['link'] = import_id
                
                relative_file = proper_path.replace(full_base_directory, "")
                queue.insert(0, relative_file)

        file_data['real_path'] = backend_file.replace(full_build_directory, ".")

        build_external_imports(result, build_directory, lang, files)

    for be_item in be_map.items():
        file = be_item[0]
        content = be_item[1]["code"]
        content = link_code(content, be_item[1]['imports'], files_by_id, full_base_directory)
        files.write(file, content)

        for path in be_item[1]['imports']:
            if path['type'] == 'external':
                lib_list = path['library'].split("/")
                library_path = CURRENT_DIRECTORY + "/../" + lib_list[0] + "/" + path['lang'] + "/" + path['env'] + "/" + lib_list[1] + "." + path['extension']
                full_library_path = files.abspath(library_path)

                build_lib_dir = full_build_directory + "/" + lib_list[0]
                if not files.exists(build_lib_dir):
                    files.mkdir(build_lib_dir)

                result_path = "/" + lib_list[0] + "/" + lib_list[1] + "_" + path['lang'] + "_" + path['env'] + "." + path['extension']
                full_result_path = full_build_directory + result_path
                files.copy(full_library_path, full_result_path)

    for fe_item in fe_map.items():
        file = fe_item[0]
        content = fe_item[1]["code"]
        files.write(file, content)
        content = link_code(content, fe_item[1]['imports'], files_by_id, full_base_directory)
        files.write(file, content)

        for path in fe_item[1]['imports']:
            if path['type'] == 'external':
                lib_list = path['library'].split("/")
                library_path = CURRENT_DIRECTORY + "/../" + lib_list[0] + "/" + path['lang'] + "/" + path['env'] + "/" + lib_list[1] + "." + path['extension']
                full_library_path = files.abspath(library_path)

                build_lib_dir = full_build_directory + "/" + lib_list[0]
                if not files.exists(build_lib_dir):
                    files.mkdir(build_lib_dir)

                result_path = "/" + lib_list[0] + "/" + lib_list[1] + "_" + path['lang'] + "_" + path['env'] + "." + path['extension']
                full_result_path = full_build_directory + result_path
                files.copy(full_library_path, full_result_path)

def _script_dir(files):
    return files.dirname(files.transpilerPath())

def _get_library(libType, lang, env, library, files):
    extension = _FILE_ENDINGS[lang]
    libPath = files.abspath(_script_dir(files) + "/" + libType + "/" + lang + "/" + env + "/" + library + "." + extension)
    return files.read(libPath)

def _get_new_lib_path(libType, lang, category, library, buildDir, files):
    extension = _FILE_ENDINGS[lang]
    newLibFile = libType + "_" + lang + "_" + category + "_" + library + "." + extension
    newLibPath = files.abspath(buildDir + "/" + newLibFile)
    return newLibPath

def _copy_library(libType, lang, env, library, build_dir, files):
    data = _get_library(libType, lang, env, library, files)
    new_path = _get_new_lib_path(libType, lang, env, library, build_dir, files)
    files.write(new_path, data)

def build_external_imports(result, build_dir, lang, files):
    manifest_file = files.abspath(build_dir) + "/manifest.json"
    manifest = []
    if files.exists(manifest_file):
        manifest_data = files.read(manifest_file)
        manifest = json.loads(manifest_data)

    if result['code']['frontend']:
        if "frontend_framework" not in manifest:
            _copy_library('stdlib', lang, 'backend', 'webapp.tmpl', build_dir, files)
            manifest.append('frontend_framework')
        # also need common backend
        if "stdlib_common_backend" not in manifest:
            _copy_library('stdlib', lang, 'backend', 'common', build_dir, files)
            manifest.append('stdlib_common_backend')

    files.write(manifest_file, json.dumps(manifest))
