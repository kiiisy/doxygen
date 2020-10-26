import sys
import re
from tkinter import messagebox


REGEX_FUNCTION_NAME = r'^(?!static).*\(.*\)$'
REGEX_BRIEF = r'//\s*概\s要：(.*)$'
REGEX_DETAILS = r'//\s*機\s能：(.*)$'
REGEX_PARAM = r'//\s*引\s数：(.*)$'
REGEX_RETRUN = r'//\s*戻り値：(.*)$'
REGEX_BLANK =  r'//\s*：(.*)$'
REGEX_DOXYGEN_CHECK = r'\*\s@brief.*$'
COMMENT_LENGTH_MIN = 1
END_POINT = '/*\n'


class RegularExpression:
    def __init__(self, items, regex: str):
        self.__items = items
        self.__regex = regex

    def get_target_name_and_index(self) -> dict:
        name_and_index = {}
        for index, item in enumerate(self.__items):
            if re.match(self.__regex, item):
                name_and_index.update([(item, index)])
        return name_and_index

    def create_comment(self) -> list:
        comment = []
        try:
            current_comment_len = len(self.__items)
            if current_comment_len > COMMENT_LENGTH_MIN:
                comment.append(re.match(self.__regex, self.__items[0]))
                for item in self.__items[1:]:
                    comment.append(re.match(REGEX_BLANK, item))
            else:
                comment.append(re.match(self.__regex, self.__items[0]))
            return comment
        except TypeError:
            messagebox.showerror('エラー', '前提条件違反です。処理を終了します。')
            sys.exit()

    def exist(self, index=None):
        if index == None:
            return True if re.match(self.__regex, self.__items) else False
        else:
            return True if re.match(self.__regex, self.__items[index]) else False

    @classmethod
    def not_exist(cls, target_lists, target_index):
        for target_list in target_lists[target_index::-1]:
            if target_list != END_POINT:
                doxygen_comment = cls(target_list, REGEX_DOXYGEN_CHECK)
                if doxygen_comment.exist():
                    return False
        return True