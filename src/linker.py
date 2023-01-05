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
    return generate_and_link_inner(starting_files, build_directory, base_directory, File)

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
        queue.append(relative_file)

    while len(queue) > 0:
        file = queue.pop()
        full_file = full_base_directory + "/" + file

        contents = files.read(full_file)

        tree = parse_statement(contents)
        processed = process_tree(tree)
        preprocessed = preprocess(processed)
        result = generate(preprocessed, lang)

        backend_file = full_build_directory + "/" + file + "_backend." + _FILE_ENDINGS[lang]
        files.write(backend_file, result['code']['backend'])

        frontend_file = full_build_directory + "/" + file + "frontend." + _FILE_ENDINGS[lang]
        files.write(frontend_file, result['code']['frontend'])

