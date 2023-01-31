from file import File
from grammar import parse_statement
from transformer import process_tree
from preprocessor import preprocess
from generator import generate

# turn to true for debug logs
LOG = False

def log(str):
    if LOG:
        print(str)

def link_code(code, be_imports, files_by_id, base_directory):
    for path in be_imports:
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
    for file in starting_files:
        full_file = files.abspath(file)
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
                proper_path = files.abspath(file_directory + item['path'])
                import_id = _get_id_for_file(proper_path)
                be_map[backend_file]["code"] = be_map[backend_file]["code"].replace(item['link'], import_id)
                item['link'] = import_id
                
                relative_file = proper_path.replace(full_base_directory, "")
                queue.insert(0, relative_file)

        file_data['real_path'] = backend_file.replace(full_build_directory, ".")

    for be_item in be_map.items():
        file = be_item[0]
        content = be_item[1]["code"]
        content = link_code(content, be_item[1]['imports'], files_by_id, full_base_directory)
        files.write(file, content)

    for fe_item in fe_map.items():
        file = fe_item[0]
        content = fe_item[1]["code"]
        files.write(file, content)

