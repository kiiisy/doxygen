import tkinter as tk
from tkinter import ttk, messagebox
import option as op
import regular_expression as re
import error_check as eck
import button_proc as btnproc
import file_proc as fproc
import const


class TKroot(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('doxygen')
        self.geometry('1000x300')
        #self.config(bg = 'light gray')


class Application(tk.Frame):
    def __init__(self, master = None, **kwargs):
        super().__init__(master, **kwargs)
        self.__target_name = tk.StringVar()
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
        f1_button = tk.Button(f1, 
            text = 'update',
            width = 5,
            command = self.update)
        f1_button.grid(row = 0, column = 2, ipadx = 30, ipady = 10, padx = 20)
        #---------------------------------------------------------------------

        #create frame 2. -----------------------------------------------------
        f2 = tk.Frame(self)
        f2.place(width = 1000, y = 64, x = 20)
        f2_label = tk.Label(f2, text = 'function name')
        f2_label.grid(row = 0, column = 0, ipadx = 20)
        self.__target_name.set('')
        self.__f2_opt = tk.OptionMenu(f2, self.__target_name, '')
        self.__f2_opt.config(width = 80)
        self.__f2_opt.grid(row = 0, column = 1, padx = 10)
        self.__all_target_state.set(False)
        f2_chk_button = tk.Checkbutton(f2,
            text = '全対象',
            variable = self.__all_target_state)
        f2_chk_button.grid(row = 0, column = 2, ipady = 10, padx = 20)
        #---------------------------------------------------------------------

        #create frame 3. -----------------------------------------------------
        f3 = tk.Frame(self)
        f3.place(width = 150, x = 10, y = 120, height = 500)
        for i in range(const.WIDGET_NUMBER):
            self.__comment.append(tk.StringVar())
            self.__comment[i].set(const.DOXYGEN_COMMAND[i])
            self.f3_cb = ttk.Combobox(f3, textvariable = self.__comment[i], 
                                            values = const.DOXYGEN_COMMAND,
                                            width = 10,
                                            state = 'readonly')
            self.f3_cb.grid(pady = 4, padx = 20)
        #---------------------------------------------------------------------

        #create frame 4. -----------------------------------------------------
        f4 = tk.Frame(self)
        f4.place(width = 660, x = 160, y = 120, height = 500)
        for i in range(const.WIDGET_NUMBER):
            self.__entry_values.append(tk.StringVar())
            self.f4_entry = tk.Entry(f4,
                width = 80,
                textvariable = self.__entry_values[i])
            self.f4_entry.grid(pady = 4)
        #---------------------------------------------------------------------

        #create frame 5. -----------------------------------------------------
        f5 = tk.Frame(self)
        f5.place(width = 140, x = 830, y = 120, height = 180)
        f5_option_button = tk.Button(f5, text = 'option', width = 10,
            height = 0, command = self.option)
        f5_option_button.grid(row = 0, pady = 20)
        f5_run_button = tk.Button(f5, 
            text = 'run',
            width = 10,
            height = 2,
            command = lambda :self.run(comment = self.__comment,
                target_name = self.__target_name, 
                entry_values = self.__entry_values,
                save_type = self.sub_f2_chk_button))
        f5_run_button.grid(row = 1, padx = 20, ipady = 10)
        #---------------------------------------------------------------------

    def update(self):
        file_path = self.__update_error_check(self.__file_path.get())
        if file_path.exist():
            target_file = self.__extraction(self.__file_path.get())
            extracted_contents = target_file.extract()
            opt = self.__f2_opt['menu']
            opt.delete(0, 'last')
            for content in extracted_contents:
                opt.add_command(label = content.strip(), 
                    command = tk._setit(self.__target_name, content))
            self.__target_name.set(extracted_contents[0])

    def run(self, **kwargs):
        # If this available, you can check 
        # before-error which is doxygen 
        # already exist in this code.
        '''
        file_contents = self.__read_items()
        doxygen_comment = self.__run_error_check(file_contents)
        all_target_is_checked = self.__get_all_target_state()
        all target button is checked and doxyten comment exists. 
        if doxygen_comment.exist() and all_target_is_checked:
            messagebox.showerror('警告', 'コード内にDoxygenコメントが存在しています')
            return
        '''
        all_or_part = self.__judge_all_or_part(**kwargs)
        all_or_part.insert_(self.__file_path)
        messagebox.showinfo('通知', '完了しました')

    def option(self):
        op_root = op.TKTopLevel()
        op_app = op.Application(master = op_root, 
                                parent = self,
                                width = 500,
                                height = 300)
        op_app.mainloop

    def __judge_all_or_part(self, **kwargs):
        all_target_state = self.__get_all_target_state()
        if all_target_state is True:
            return self.__all(**kwargs)
        else:
            return self.__part(**kwargs)

    def __read_items(self):
        file_path = self.__file_path.get()
        read_type = self.__read(file_path)
        return fproc.execute(read_type)

    def __extraction(self, file_path):
        #instance Extraction class
        return btnproc.Extraction(self.sub_f1_entry, file_path)

    def __part(self, **kwargs):
        #instance Part class
        return btnproc.Part(**kwargs)

    def __all(self, **kwargs):
        #instance All class
        return btnproc.All(**kwargs)

    def __get_all_target_state(self):
        return self.__all_target_state.get()

    def __run_error_check(self, file_path):
        #instance RunCheck class
        return eck.RunErrorCheck(file_path)

    def __update_error_check(self, file_path):
        #instance Check class
        return eck.UpdateErrorCheck(file_path)

    def __read(self, file_path):
        #instance Read class
        return fproc.Read(file_path)

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

    def __save_type(self, save_type):
        return op.SaveType(save_type)