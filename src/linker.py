def link_code(code, be_imports, all_files):
    for path in be_imports:
        real_file_path = all_files[path]
        code = code.replace("<<<{}>>>".format(path), real_file_path)

    return code