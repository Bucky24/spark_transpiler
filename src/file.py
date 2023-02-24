import os
import shutil

class File:
    @classmethod
    def read(cls, filename):
        handle = open(filename, "r")
        contents = handle.read()
        handle.close()
        return contents
    
    @classmethod
    def write(cls, filename, contents):
        handle = open(filename, "w")
        handle.write(contents)
        handle.close()

    @classmethod
    def abspath(cls, file):
        return os.path.abspath(file)

    @classmethod
    def dirname(cls, file):
        return os.path.dirname(file)

    @classmethod
    def exists(cls, file):
        return os.path.exists(file)

    @classmethod
    def mkdir(cls, dir):
        return os.mkdir(dir)
    
    @classmethod
    def copy(cls, src, to):
        shutil.copyfile(src, to)

class FileMock:
    @classmethod
    def reset(cls):
        cls.mocks = {
            "paths": {},
            "data": {},
            "written": {},
            "exists": [],
            "mkdir": [],
        }

    @classmethod
    def abspath_set(cls, base, result):
        cls.mocks["paths"][base] = result

    @classmethod
    def abspath(cls, file):
        if file[0] == "/":
            return file

        if file in cls.mocks["paths"]:
            return cls.mocks["paths"][file]
        raise Exception("No abspath mock for {}".format(file))

    @classmethod
    def read_set(cls, filename, data):
        cls.mocks["data"][filename] = data

    @classmethod
    def read(cls, filename):
        if filename in cls.mocks["data"]:
            return cls.mocks["data"][filename]
        raise Exception("No read mock for {}".format(filename))
    
    @classmethod
    def write(cls, filename, contents):
        if filename not in cls.mocks["written"]:
            cls.mocks["written"][filename] = ""
        cls.mocks["written"][filename] += contents

    @classmethod
    def get_write(cls, filename):
        if filename in cls.mocks["written"]:
            return cls.mocks["written"][filename]
        return None

    @classmethod
    def dirname(cls, filename):
        path_arr = filename.split("/")
        path_arr.pop()
        return "/".join(path_arr) + "/"

    @classmethod
    def exists_set(cls, file):
        cls.mocks['exists'].add(file)

    @classmethod
    def exists(cls, file):
        return file in cls.mocks['exists']

    @classmethod
    def mkdir(cls, dir):
        cls.mocks['mkdir'].append(dir)

    @classmethod
    def mkdir_get(cls):
        return cls.mocks['mkdir']
