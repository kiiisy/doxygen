import tkinter as tk
import regular_expression as re


class TKTopLevel(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title('詳細設定')
        self.geometry('500x300')


class Application(tk.Frame):
    def __init__(self, master = None, parent = None, **kwargs):
        super().__init__(master, **kwargs)
        self.parent = parent
        self.master = master
        self.regular_expression = tk.StringVar()
        self.__save_type_state = tk.BooleanVar()
        self.create_widget()
        self.pack()

    def create_widget(self):
        #create frame 1
        self.f1 = tk.Frame(self, relief = tk.GROOVE, bd = 3)
        self.f1.place(width = 500, height = 50, y = 10)
        self.f1_label = tk.Label(self.f1, text = '正規表現')
        self.f1_label.grid(row = 0, column = 0, pady = 5)
        self.f1_entry = tk.Entry(self.f1, width = 40, textvariable = self.regular_expression)
        self.f1_entry.insert(0, re.REGEX_FUNCTION_NAME)
        self.f1_entry.grid(row = 0, column = 1, padx = 20, pady = 5)

        #create frame 2
        self.f2 = tk.Frame(self, relief = tk.GROOVE, bd = 3)
        self.f2.place(width = 500, height = 50, y = 80)
        self.f2_label = tk.Label(self.f2, text = '上書き保存')
        self.f2_label.grid(row = 0, column = 0, pady = 5)
        self.__save_type_state.set(False)
        self.f2_chk_button = tk.Checkbutton(self.f2,
            variable = self.__save_type_state)
        self.f2_chk_button.grid(row = 0, column = 1, padx = 20, pady = 5)

        #create frame 4
        self.f4 = tk.Frame(self, relief = tk.GROOVE, bd = 3)
        self.f4.place(width = 500, height = 40, y = 250)
        self.f4_button = tk.Button(self.f4, text = '完了', command = self.complete)
        self.f4_button.grid(padx = 380, ipadx = 30)

    def complete(self):
        self.parent.sub_f1_entry = self.regular_expression.get()
        self.parent.sub_f2_chk_button = self.__save_type_state.get()
        self.master.destroy()


class SaveType:
    def __init__(self, type_):
        self.__overwrite = type_

    def is_checked(self):
        if self.__overwrite:
            return True
        else:
            return False