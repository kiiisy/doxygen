import regular_expression as re
import file_proc as fproc
import const


class Extraction:
    def __init__(self, regex, file_path):
        self.__file_path = file_path
        self.__regex = (re.REGEX_FUNCTION_NAME if regex is None else regex)

    def extract(self):
        target_lists = self.__read_items()
        file_contens = self.__edit_items(target_lists)
        return file_contens

    def __read_items(self):
        file_path = self.__file_path
        read_type = self.__read(file_path)
        return fproc.execute(read_type)

    def __edit_items(self, target_lists):
        edited_lists = []
        regular_expression = self.__regular_expression(
            items = target_lists, 
            regex = self.__regex)
        target_dict = regular_expression.get_target_name_and_index()
        for target_name, target_index in target_dict.items():
            if self.__not_exist_doxygen(target_lists, target_index):
                edited_lists.append(target_name)
        return edited_lists

    def __not_exist_doxygen(self, target_list, target_index):
        return re.RegularExpression.not_exist(target_list, target_index)

    def __read(self, file_path):
        #instance Read class
        return fproc.Read(file_path)

    def __regular_expression(self, *, items, regex):
        #instance RegularExpression class
        return re.RegularExpression(items, regex)


class Insertion(object):
    def insert_(self, file_path):
        raise 'call abstract method'

    def _read_contents(self, file_path):
        read_type = self.__read(file_path)
        return fproc.execute(read_type)

    def _get_function_index(self, file_contents, function_name):
        return (file_contents.index(function_name))

    def _set_contents(self, file_path, edited_file_contents, save_type):
        write_type = self.__write(file_path, edited_file_contents, save_type)
        fproc.execute(write_type)

    def _list(self, file_contens):
        #instance List class
        return List(file_contens)

    def __read(self, file_path):
        #instance Read class
        return fproc.Read(file_path)

    def __write(self, file_path, *arg):
        #instance Write class
        return fproc.Write(file_path, *arg)


class Part(Insertion):
    def __init__(self, **kwargs):
        self.__kwargs = kwargs.copy()
        self.__target_name = kwargs.get('target_name').get()
        self.__save_type = kwargs.get('save_type')

    def insert_(self, file_path):
        file_path_ = file_path.get()
        file_contents = super()._read_contents(file_path_)
        if file_contents is None:
            return False
        list_ = super()._list(file_contents)
        target_index = super()._get_function_index(
            file_contents,
            self.__target_name)
        edited_file_contents = list_.create_part(
            target_index,
            **self.__kwargs)
        super()._set_contents(
            file_path_,
            edited_file_contents,
            self.__save_type)
        return True


class All(Insertion):
    def __init__(self, **kwargs):
        self.__save_type = kwargs.get('save_type')

    def insert_(self, file_path):
        file_path_ = file_path.get()
        file_contents = super()._read_contents(file_path_)
        if file_contents is None:
            return False
        list_ = super()._list(file_contents)
        regex = self.__regular_expression(
            items = file_contents,
            regex = re.REGEX_FUNCTION_NAME)
        target_dict = regex.get_target_name_and_index()
        edited_file_contents = list_.create_all(target_dict)
        super()._set_contents(
            file_path_,
            edited_file_contents,
            self.__save_type)
        return True

    def __regular_expression(self, *, items, regex):
        #instance RegularExpression class
        return re.RegularExpression(items, regex)


class List:
    def __init__(self, input_file_contens):
        self.__doxygen_comment = []
        self.__input_file_contents = input_file_contens

    def create_part(self, function_index, **kwargs):
        comment = self.__comment()
        self.__doxygen_comment = comment.create_part(**kwargs)
        file_contents = self.__input_file_contents
        for i in range(len(self.__doxygen_comment)):
            #対象の後ろに入れるため+1する
            file_contents.insert(function_index + 1 , self.__doxygen_comment[i])
        return file_contents

    def create_all(self, target_dict):
        before_file_contents = self.__input_file_contents
        after_file_contents = self.__input_file_contents.copy()
        comment_cnt = 0
        for target_index in target_dict.values():
            comment = self.__comment() 
            if self.__not_exist_doxygen(before_file_contents, target_index):
                self.__doxygen_comment = comment.create_all(
                    before_file_contents,
                    target_index)
                after_file_contents[
                    (target_index) + comment_cnt:
                    (target_index) + comment_cnt] = self.__doxygen_comment
            comment_cnt += comment.get_doxygen_comment_number()
        return after_file_contents

    def __not_exist_doxygen(self, target_list, target_index):
        return re.RegularExpression.not_exist(target_list, target_index)

    def __comment(self, **kwargs):
        #instance Comment class
        return Comment(**kwargs)


class Comment:
    def __init__(self):
        self.__doxygen_comment = []

    def create_part(self, **kwargs):
        self.__doxygen_comment.append(const.START_COMMENT)
        for i in range(const.WIDGET_NUMBER):
            self.__doxygen_comment.append('*'
                + ' '
                + kwargs.get('comment')[i].get()
                + ' '
                + kwargs.get('entry_values')[i].get()
                + '\n')
        self.__doxygen_comment.append(const.END_COMMENT)
        return self.__doxygen_comment

    def create_all(self, file_contents, target_index):
        lookup = self.__lookup(target_index)
        return self.__create_comment_list(file_contents, lookup)

    def get_doxygen_comment_number(self):
        return len(self.__doxygen_comment)

    def __create_comment_list(self, file_contents, object_):
        self.__doxygen_comment.append(const.START_COMMENT)
        regex_lists = [
                        re.REGEX_BRIEF, re.REGEX_DETAILS,
                        re.REGEX_PARAM, re.REGEX_RETRUN] 
        for regex_list in regex_lists:
            comments = self.__edit_comments(object_, file_contents, regex_list)
            self.__create_list(comments)
        self.__doxygen_comment.append(const.END_COMMENT)
        return self.__doxygen_comment

    def __create_list(self, comments):
        [self.__doxygen_comment.append(comment) for comment in comments]

    def __edit_comments(self, object_, file_contents, regex):
        fixed_comment = []
        before_list = object_.get_comment(file_contents, regex)
        regular_expression = self.__regular_expression(
            items = before_list,
            regex = regex)
        comments = regular_expression.create_comment()
        selected_command = self.__select_doxygen_command(regex)
        for comment in comments:
            fixed_comment.append(('*'
                                + ' ' 
                                + selected_command
                                + ' ' 
                                + comment.group(1)
                                + '\n'))
        return fixed_comment

    def __select_doxygen_command(self, regex):
        if regex == re.REGEX_BRIEF:
            return const.DOXYGEN_COMMAND[0]
        if regex == re.REGEX_DETAILS:
            return const.DOXYGEN_COMMAND[1]
        if regex == re.REGEX_PARAM:
            return const.DOXYGEN_COMMAND[2]
        if regex == re.REGEX_RETRUN:
            return const.DOXYGEN_COMMAND[3]

    def __lookup(self, target_index):
        #instance Lookup class
        return Lookup(target_index)

    def __regular_expression(self, *, items, regex):
        #instance RegularExpression class
        return re.RegularExpression(items, regex)


class Lookup:
    def __init__(self, target_index):
        self.__target_index = target_index

    def get_comment(self, file_contents, comment_type):
        return_comments = []
        for file_content, index in self.__reverse(file_contents):
            if file_content != re.END_POINT:
                comment = self.__regular_expression(
                    items = file_contents,
                    regex = comment_type)
                if comment.exist(index):
                    return_comments.append(file_content)
                    blank_comment = self.__get_blank_comment(file_contents, index)
                    return_comments.extend(blank_comment)
                    return return_comments
        return None

    def __get_blank_comment(self, file_contents, target_index):
        return_comments = []
        #空白を調べるために対象のインデックスから+1する
        blank_index = target_index + 1
        for file_content in file_contents[blank_index:]:
            blank_comment =\
                self.__regular_expression(
                    items = file_content,
                    regex = re.REGEX_BLANK)
            if blank_comment.exist():
                return_comments.append(file_content)
            else:
                break
        return return_comments

    def __reverse(self, file_contents):
        #ループ処理での初回-1の調整のために+1する
        index = self.__target_index + 1
        for file_content in file_contents[self.__target_index::-1]:
            index-=1
            yield file_content, index

    def __regular_expression(self, *, items, regex):
        #instance RegularExpression class
        return re.RegularExpression(items, regex)