import os
from tkinter import messagebox
import regular_expression as re


class UpdateErrorCheck:
    def __init__(self, file_path):
        self.__file_path = file_path

    def exist(self):
        if os.path.exists(self.__file_path):
            return True
        else:
            messagebox.showerror('警告', 'ファイルが見つかりません')
            return False


class RunErrorCheck:
    def __init__(self, file_contents):
        self.__file_contents = file_contents

    def exist(self):
        for file_content in self.__file_contents:
            doxygen_comment =\
                self.__regular_expression(file_content, re.REGEX_DOXYGEN_CHECK)
            if doxygen_comment.exist():
                return True
        return False

    def __regular_expression(self, items, regex):
        #instance RegularExpression class
        return re.RegularExpression(items, regex)