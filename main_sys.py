import sys
import abc
import re
import copy
import os
import tkinter as tk
from tkinter import ttk, messagebox
import sub_sys

#test path
test_path = '/Users/kisa/PYTHON/01_Practice/tmp/test.c'
#----------------------------------------
WIDGET_NUMBER = 4                                                #doxygenコメント数
REGEX_FUNCTION_NAME = r'^(?!static).*\(.*\)$'                    #正規表現(C対応)
REGEX_BRIEF = r'//\s*概\s要：(.*)$'
REGEX_DETAILS = r'//\s*機\s能：(.*)$'
REGEX_PARAM = r'//\s*引\s数：(.*)$'
REGEX_RETRUN = r'//\s*戻り値：(.*)$'
REGEX_BRANK =  r'//\s*：(.*)$'
#REGEX_BRIEF = r'\*\s*ABSTRACT\s*：(.*)$'
#REGEX_DETAILS = r'\*\s*FUNCTION\s*：(.*)$'
#REGEX_PARAM = r'\*\s*ARGUMENT\s*：(.*)$'
#REGEX_RETRUN = r'\*\s*RETURN\s*：(.*)$'
#REGEX_BRANK =  r'\*\s*：(.*)$'
COMMENT_LENGTH_MIN = 1
END_MARK = '/*\n'

doxygen_comment = ['@brief', '@details', '@param', '@return']

class TKroot(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('doxygen')
        self.geometry('1000x300')
        #self.config(bg = 'light gray')


class Application(tk.Frame):
    def __init__(self, master = None, **kwargs):
        super().__init__(master, **kwargs)
        self.__function_name = tk.StringVar()
        self.__file_path = tk.StringVar()
        self.__entry_values = []
        self.__comment = []
        self.__all_target_state = tk.BooleanVar()
        self.__sub_f1_entry = None
        self.__sub_f2_chk_button = None
        self.create_widget()
        self.pack()

    def create_widget(self): 
        #create frame 1. -----------------------------------------------------
        f1 = tk.Frame(self)
        f1.place(relheight = 0.1, width = 1000, height = 50, x = 20)
        f1_label = tk.Label(f1, text = 'path')
        f1_label.grid(row = 0, column = 0, ipadx = 50, pady = 25)
        f1_entry = tk.Entry(f1, width = 80, textvariable = self.__file_path)
        f1_entry.grid(row = 0, column = 1, padx = 10)
        f1_button = tk.Button(f1, text = 'update', width = 5, 
            command = self.update)
        f1_button.grid(row = 0, column = 2, ipadx = 30, ipady = 10, padx = 20)
        #---------------------------------------------------------------------

        #create frame 2. -----------------------------------------------------
        f2 = tk.Frame(self)
        f2.place(width = 1000, y = 64, x = 20)
        f2_label = tk.Label(f2, text = 'function name')
        f2_label.grid(row = 0, column = 0, ipadx = 20)
        self.__function_name.set('')
        self.__f2_opt = tk.OptionMenu(f2, self.__function_name, '')
        self.__f2_opt.config(width = 80)
        self.__f2_opt.grid(row = 0, column = 1, padx = 10)
        self.__all_target_state.set(False)
        f2_chk_button = tk.Checkbutton(f2, text = '全対象',
            variable = self.__all_target_state)
        f2_chk_button.grid(row = 0, column = 2, ipady = 10, padx = 20)
        #---------------------------------------------------------------------

        #create frame 3. -----------------------------------------------------
        f3 = tk.Frame(self)
        f3.place(width = 150, x = 10, y = 120, height = 500)
        global doxygen_comment
        for i in range(WIDGET_NUMBER):
            self.__comment.append(tk.StringVar())
            self.__comment[i].set(doxygen_comment[i])
            self.f3_cb = ttk.Combobox(f3, textvariable = self.__comment[i], 
                values = doxygen_comment, width = 10, state = 'readonly')
            self.f3_cb.grid(pady = 4, padx = 20)
        #---------------------------------------------------------------------

        #create frame 4. -----------------------------------------------------
        f4 = tk.Frame(self)
        f4.place(width = 660, x = 160, y = 120, height = 500)
        for i in range(WIDGET_NUMBER):
            self.__entry_values.append(tk.StringVar())
            self.f4_entry = tk.Entry(f4, width = 80,
                textvariable = self.__entry_values[i])
            self.f4_entry.grid(pady = 4)
        #---------------------------------------------------------------------

        #create frame 5. -----------------------------------------------------
        f5 = tk.Frame(self)
        f5.place(width = 140, x = 830, y = 120, height = 180)
        f5_option_button = tk.Button(f5, text = 'option', width = 10,
            height = 0, command = self.option)
        f5_option_button.grid(row = 0, pady = 20)
        f5_run_button = tk.Button(f5, text = 'run', width = 10,
            height = 2, command = lambda :self.run(comment = self.__comment,
            function_name = self.__function_name, 
            entry_values = self.__entry_values,
            save_type = self.sub_f2_chk_button))
        f5_run_button.grid(row = 1, padx = 20, ipady = 10)
        #---------------------------------------------------------------------

    def update(self):
        file_path = self.__updatecheck(self.__file_path.get())
        if file_path.exsist():
            extraction = self.__extraction(self.__file_path.get())
            file_contents = extraction.manage(Read)
            opt = self.__f2_opt['menu']
            opt.delete(0, 'last')
            for file_content in file_contents:
                opt.add_command(label = file_content.strip(), 
                    command = tk._setit(self.__function_name, file_content))
            self.__function_name.set(file_contents[0])

    def run(self, **kwargs):
        all_or_partof = self.__judge_all_or_partof(**kwargs)
        file_path = self.__file_path.get()
        doxygen_comment = self.__runcheck(file_path)
        if doxygen_comment.exsist():
            messagebox.showerror('警告', 'コード内にDoxygenコメントが存在しています')
            return
        all_or_partof.manage(self.__file_path)
        messagebox.showinfo('通知', '完了しました')

    def __extraction(self, file_path):
        #instance Extraction class
        return Extraction(self.sub_f1_entry, file_path)

    def __partof(self, **kwargs):
        #instance PartOf class
        return PartOfInsertion(**kwargs)

    def __all(self, **kwargs):
        #instance All class
        return AllInsertion(**kwargs)

    def __get_all_target_state(self):
        return self.__all_target_state.get()

    def __runcheck(self, file_path):
        #instance RunCheck class
        return RunCheck(file_path)

    def __updatecheck(self, file_path):
        #instance Check class
        return UpdateCheck(file_path)

    def __judge_all_or_partof(self, **kwargs):
        all_target_state = self.__get_all_target_state()
        if all_target_state is True:
            return self.__all(**kwargs)
        else:
            return self.__partof(**kwargs)

    def option(self):
        #Here is a sub system
        self.sub_root = sub_sys.TKTopLevel()
        self.sub_app = sub_sys.Application(master = self.sub_root,
            parent = self, width = 500, height = 300)

    @property
    def sub_f1_entry(self):
        return self.__sub_f1_entry

    @sub_f1_entry.setter
    def sub_f1_entry(self, sub_f1_entry):
        self.__sub_f1_entry = sub_f1_entry

    @property
    def sub_f2_chk_button(self):
        return self.__sub_f2_chk_button

    @sub_f2_chk_button.setter
    def sub_f2_chk_button(self, sub_f2_chk_button):
        self.__sub_f2_chk_button = sub_f2_chk_button


class Extraction:
    def __init__(self, regex, file_path):
        self.__file_path = file_path
        self.__file_contents = None
        self.regular_expression = (REGEX_FUNCTION_NAME if 
            regex is None else regex)

    def __get_items(self, file_type_):
        file_type = self.__file_type(file_type_)
        return file_type.execute()

    def __set_items(self, function_list):
        regular_expression = self.__regular_expression()
        self.__file_contents = regular_expression.get_function_name(
            function_list, self.regular_expression)

    def manage(self, file_type):
        self.__set_items(self.__get_items(file_type))
        return self.__file_contents

    def __file_type(self, file_type, *args):
        #instance Write or Read class
        return file_type(self.__file_path)

    def __regular_expression(self):
        #instance RegularExpression class
        return RegularExpression()


class RegularExpression:
    def get_function_name(self, items, regular_expression):
        return [s for s in items if re.match(regular_expression, s)]

    def get_function_name_and_index(self, items, regular_expression):
        name_and_index = {}
        for index, item in enumerate(items):
            if re.match(regular_expression, item):
                name_and_index.update([(item, index)])
        return name_and_index

    def create_comment(self, items, regular_expression):
        comment = []
        try:
            if len(items) > COMMENT_LENGTH_MIN:
                comment.append(re.match(regular_expression, items[0]))
                for item in items[1:]:
                    comment.append(re.match(REGEX_BRANK, item))
            else:
                comment.append(re.match(regular_expression, items[0]))
            return comment
        except TypeError:
            messagebox.showerror('エラー', '前提条件違反です。処理を終了します。')
            sys.exit()

    def exist(self, items, regular_expression, index=None, cnt=None):
        if index == None or cnt == None:
            return True if re.match(regular_expression, items) else False
        else:
            return True if re.match(regular_expression, 
                items[index - cnt]) else False 


class FileType(abc.ABC):
    @abc.abstractclassmethod
    def lines(self):
        pass

    def execute(self):
        lines = self.lines()
        return lines


class Write(FileType):
    def __init__(self, file_path, *args):
        self.__file_path = file_path
        self.__input_contents = args[0]
        self.__file_contens = []
        self.__overwrite_button = self.__writecheck(args[1])

    def lines(self):
        if self.__overwrite_button.is_checked():
            file_path = self.__file_path
        else:
            file_path = (os.path.dirname(self.__file_path) + '/'
                + os.path.splitext(os.path.basename(self.__file_path))[0]
                + '_d' + '.c')
        with FileAccess(file_path, 'w') as file:
            file.writelines(self.__input_contents)
        return None

    def __writecheck(self, save_type):
        return WriteCheck(save_type)


class Read(FileType):
    def __init__(self, file_path, *args):
        self.__file_path = file_path

    def lines(self):
        with FileAccess(self.__file_path, 'r') as file:
            file_contents = file.readlines()
        return file_contents


class FileAccess(object):
    def __init__(self, file_path, file_open_type):
        self._file_path = file_path
        self._file_open_type = file_open_type
        self._file = None

    def _open(self):
        self._file = open(self._file_path, self._file_open_type)
        #self._file = open(test_path, self._file_open_type)

    def _close(self):
        self._file.close()

    def __enter__(self):
        self._open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._close()

    def readlines(self):
        file_contens = []
        contens = self._file.readline()
        while contens:
            file_contens.append(contens)
            contens = self._file.readline()
        return file_contens

    def writelines(self, values):
        self._file.writelines(values)


class WriteCheck:
    def __init__(self, save_type):
        self.__overwrite = save_type

    def is_checked(self):
        if self.__overwrite:
            return True
        else:
            return False


class Insertion(object):
    def __init__(self):
        self.file_contents = []
        self.function_index = None

    def manage(self, file_path):
        raise 'call abstract method'

    def _get_contents(self, file_type, file_path):
        self.__file_type(file_type, file_path)
        self.file_contents = self.file_type.execute()

    def _get_function_index(self, file_contents, function_name):
        self.function_index = (file_contents.index(function_name))

    def _set_contents(self, file_type, file_path, file_contents, save_type):
        self.__file_type(file_type, file_path, file_contents, save_type)
        return self.file_type.execute()

    def __file_type(self, file_type, file_path, *args):
        #instance Write or Read class
        self.file_type = file_type(file_path, *args)

    def _list(self, file_contens):
        #instance List class
        return List(file_contens)


class PartOfInsertion(Insertion):
    def __init__(self, **kwargs):
        self.__kwargs = kwargs.copy()
        self.function_name = kwargs.get('function_name').get()
        self._save_type = kwargs.get('save_type')
        super().__init__()

    def manage(self, file_path):
        file_path_ = file_path.get()
        super()._get_contents(Read, file_path_)
        list_ = super()._list(self.file_contents)
        super()._get_function_index(self.file_contents, self.function_name)
        edited_file_contents = list_.create_partof(self.function_index,
                                                  **self.__kwargs)
        super()._set_contents(Write, file_path_, edited_file_contents,
                            self._save_type)


class AllInsertion(Insertion):
    def __init__(self, **kwargs):
        self._save_type = kwargs.get('save_type')
        super().__init__()

    def manage(self, file_path):
        file_path_ = file_path.get()
        super()._get_contents(Read, file_path_)
        list_ = super()._list(self.file_contents)
        regular_expression = self.__regular_expression()
        function_dict = regular_expression.get_function_name_and_index(
            self.file_contents, REGEX_FUNCTION_NAME)
        edited_file_contents = list_.create_all(function_dict)
        super()._set_contents(Write, file_path_, edited_file_contents,
                                self._save_type)

    def __regular_expression(self):
        #instance RegularExpression class
        return RegularExpression()


class List:
    def __init__(self, input_file_contens):
        self.__file_contents = None
        self.__doxygen_comment = []
        self.__input_file_contents = input_file_contens

    def create_partof(self, function_index, **kwargs):
        comment = self.__comment()
        self.__doxygen_comment = comment.create_partof(**kwargs)
        self.__file_contents = self.__input_file_contents
        for i in range(len(self.__doxygen_comment)):
            self.__file_contents.insert(function_index + i, 
                                        self.__doxygen_comment[i])
        return self.__file_contents

    def create_all(self, function_dict):
        self.__file_contents = self.__input_file_contents.copy()
        i = 0
        for key, value in function_dict.items():
            comment = self.__comment()
            self.__doxygen_comment = comment.create_all(
                self.__input_file_contents, key, value)
            self.__file_contents[(value) + i:(value) + i]\
                = self.__doxygen_comment
            i = i + comment.get_doxygen_comment_number()
        return self.__file_contents

    def __comment(self, **kwargs):
        #instance Comment class
        return Comment(**kwargs)


class Comment:
    def __init__(self):
        self.__doxygen_comment = []

    def __del__(self):
        pass

    def create_partof(self, **kwargs):
        self.__doxygen_comment.append('/*\n')
        for i in range(WIDGET_NUMBER):
            self.__doxygen_comment.append('*' + ' '
                + kwargs.get('comment')[i].get() + ' ' 
                + kwargs.get('entry_values')[i].get() + '\n')
        self.__doxygen_comment.append('*/\n')
        return self.__doxygen_comment

    def create_all(self, file_contents, function_name, function_index):
        lookup = self.__lookup(function_name, function_index)
        return self.__create_comment_list(file_contents, lookup)

    def __create_comment_list(self, file_contents, object_):
        self.__doxygen_comment.append('/*\n')
        regex_lists = [REGEX_BRIEF, REGEX_DETAILS, REGEX_PARAM, REGEX_RETRUN] 
        for regex_list in regex_lists:
            comments = self.__edit_comments(object_,
                                            file_contents, regex_list)
            self.__create_list(comments)
        self.__doxygen_comment.append('*/\n')
        return self.__doxygen_comment

    def __create_list(self, comments):
        for comment in comments:
            self.__doxygen_comment.append(comment)

    def __edit_comments(self, object_, file_contents, regex):
        fixed_comment = []
        before_list = object_.get_comment(file_contents, regex)
        regular_expression = self.__regular_expression()
        comments = regular_expression.create_comment(before_list, regex)
        selected_comment = self.__select_doxygen_comment(regex)
        for comment in comments:
            fixed_comment.append(('*' + ' ' 
                + selected_comment + ' ' 
                + comment.group(1) + '\n'))
        return fixed_comment

    def __select_doxygen_comment(self, regex):
        global doxygen_comment
        if regex == REGEX_BRIEF:
            return doxygen_comment[0]
        if regex == REGEX_DETAILS:
            return doxygen_comment[1]
        if regex == REGEX_PARAM:
            return doxygen_comment[2]
        if regex == REGEX_RETRUN:
            return doxygen_comment[3]

    def __lookup(self, function_name, function_index):
        #instance Lookup class
        return Lookup(function_name, function_index)

    def __regular_expression(self):
        #instance RegularExpression class
        return RegularExpression()

    def get_doxygen_comment_number(self):
        return len(self.__doxygen_comment)


class Lookup:
    def __init__(self, function_name, function_index):
        self.__function_name = function_name
        self.__function_index = function_index

    def __del__(self):
        pass

    def get_comment(self, file_contents, comment_type):
        return_comments = []
        comment = self.__regular_expression()
        i = 0
        while file_contents[self.__function_index - i] != END_MARK:
            if comment.exist(file_contents, comment_type, 
                                self.__function_index, i):
                return_comments.append(
                    file_contents[self.__function_index - i])
                brank_comment = self.__get_brank_comment(file_contents, i)
                return_comments.extend(brank_comment)
                return return_comments
            i = i + 1
        #前提条件違反の場合はNoneを返却する
        return None

    def __get_brank_comment(self, file_contents, cnt):
        return_comments = []
        brank_comment = self.__regular_expression()
        #対象を含ませないために+1とする
        hit_index = (self.__function_index - cnt) + 1
        for file_content in file_contents[hit_index:]:
            if brank_comment.exist(file_content, REGEX_BRANK):
                return_comments.append(file_content)
            else:
                break
        return return_comments

    def __regular_expression(self):
        #instance RegularExpression class
        return RegularExpression()


class UpdateCheck:
    def __init__(self, file_path):
        self.__file_path = file_path

    def exsist(self):
        if os.path.exists(self.__file_path):
            return True
        else:
            messagebox.showerror('警告', 'ファイルが見つかりません')
            return False


class RunCheck:
    def __init__(self, file_path):
        self.read = self.__read(file_path)

    def exsist(self):
        doxygen_comment = self.__regular_expression()
        file_contents = self.read.execute()
        for file_content in file_contents:
            if doxygen_comment.exist(file_content, r'\*\s@brief.*$'):
                return True
        return False

    def __read(self, file_path):
        #instance Read class
        return Read(file_path)

    def __regular_expression(self):
        #instance RegularExpression class
        return RegularExpression()


def main():
    root = TKroot()
    app = Application(master = root, width = 1000, height = 300)
    app.mainloop()

if __name__ == '__main__':
    main()
