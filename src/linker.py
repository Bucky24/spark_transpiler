from file import File
from grammar import parse_statement
from transformer import process_tree
from preprocessor import preprocess
from generator import generate

def link_code(code, be_imports, all_files):
    for path in be_imports:
        real_file_path = all_files[path]
        code = code.replace("<<<{}>>>".format(path), real_file_path)

    return code

def generate_and_link(starting_files, build_directory, base_directory, lang):
    return generate_and_link_inner(starting_files, build_directory, base_directory,lang, File)

_FILE_ENDINGS = {
    "js": "js"
}

def generate_and_link_inner(starting_files, build_directory, base_directory, lang, files):
    queue = []
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

        print("Processing " + full_file)

        file_directory = files.dirname(full_file)

        contents = files.read(full_file)

        tree = parse_statement(contents)
        processed = process_tree(tree)
        preprocessed = preprocess(processed)
        result = generate(preprocessed, lang)

        for item in result['imports']['backend']:
            if item['type'] == "path":
                proper_path = files.abspath(file_directory + item['path'])
                relative_file = proper_path.replace(full_base_directory, "")
                queue.insert(0, relative_file)
                
        backend_file = full_build_directory + file + "_backend." + _FILE_ENDINGS[lang]
        backend_code = result['code']['backend'] if result['code']['backend'] is not None else ""
        be_map[backend_file] = backend_code

        frontend_file = full_build_directory + file + "_frontend." + _FILE_ENDINGS[lang]
        frontend_code = result['code']['frontend'] if result['code']['frontend'] is not None else ""
        fe_map[frontend_file] = frontend_code

    for be_item in be_map.items():
        file = be_item[0]
        content = be_item[1]
        files.write(file, content)

    for fe_item in fe_map.items():
        file = fe_item[0]
        content = fe_item[1]
        files.write(file, content)

