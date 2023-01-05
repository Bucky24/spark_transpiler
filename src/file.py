import os

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
        return os.path(file)

class FileMock:
    @classmethod
    def reset(cls):
        cls.mocks = {
            "paths": {}
        }

    @classmethod
    def abspath_set(cls, base, result):
        cls.mocks["paths"][base] = result

    @classmethod
    def abspath(cls, file):
        if file in cls.mocks["paths"]:
            return cls.mocks["paths"][file]
        raise Exception("No abspath mock for {}".format(file))
