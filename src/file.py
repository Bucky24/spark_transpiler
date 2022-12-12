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