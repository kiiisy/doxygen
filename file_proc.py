import abc
import os
import option as op
from tkinter import messagebox

#This is for test.
#test_path = '/Users/kisa/python/04_tool/doxygen/test/test.c'


class FileType(abc.ABC):
    @abc.abstractclassmethod
    def lines(self):
        pass


class Write(FileType):
    def __init__(self, file_path, *args):
        self.__file_path = file_path
        self.__input_contents = args[0]
        self.__file_contens = []
        self.__overwrite_button = self.__save_type(args[1])

    def lines(self):
        file_path = self.__create_file_path()
        if self.__overwrite_button.is_checked():
            file_path = self.__file_path
        with FileAccess(file_path, 'w') as file:
            file.writelines(self.__input_contents)
        return None
    
    def __create_file_path(self):
        file_path = (os.path.dirname(self.__file_path)
            + '/'
            + os.path.splitext(os.path.basename(self.__file_path))[0]
            + '_d'
            + '.c')
        return file_path 

    def __save_type(self, type_):
        #inctance SaveType class.
        return op.SaveType(type_)


class Read(FileType):
    def __init__(self, file_path, *args):
        self.__file_path = file_path

    def lines(self):
        try:
            with FileAccess(self.__file_path, 'r') as file:
                file_contents = file.readlines()
            return file_contents
        except FileNotFoundError:
            messagebox.showerror('警告', 'ファイルをセットしてください')
            return None


class FileAccess(object):
    def __init__(self, file_path, file_open_type):
        self.__file_path = file_path
        self.__file_open_type = file_open_type
        self.__file = None

    def _open(self):
        self.__file = open(self.__file_path, self.__file_open_type)
        #self.__file = open(test_path, self.__file_open_type)

    def _close(self):
        self.__file.close()

    def __enter__(self):
        self._open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._close()

    def readlines(self):
        file_contents = []
        append = file_contents.append
        contents = self.__file.readline()
        while contents:
            append(contents)
            contents = self.__file.readline()
        return file_contents

    def writelines(self, values):
        self.__file.writelines(values)


def execute(file_type):
    return file_type.lines()