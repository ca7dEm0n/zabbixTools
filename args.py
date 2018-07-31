import os
import argparse
import inspect

rootPath = os.path.abspath(os.path.dirname(__file__))
baseModeDataPath = os.path.join(rootPath, 'Data')


# 返回方法的注释字典
def getDoc2Dict(func):
    doc = func.__doc__
    if doc:
        return {
            i.split(':')[0].strip(' '): i.split(':')[1]
            for i in doc.split('\n') if ':' in i
        }
    return {}


# 解析单个数据文件
def _readDataFile(file):
    file_list = []
    file_name = os.path.split(file)[-1]
    # 空文件为params类型
    if not os.path.getsize(file):
        file_list.append({
            "Parameter": "params",
            "Type": "params",
            "Description": "Params type.",
            "Function": file_name
        })
        return file_list

    with open(file) as f:
        for i in f.read().split('\n'):
            x = [_.strip('\t') for _ in i.split('|')]
            if len(x) >= 3:
                file_list.append({
                    "Parameter": x[0].strip(' '),
                    "Type": x[1].strip(' '),
                    "Description": x[2],
                    "Function": file_name
                })
    return file_list


# 获取所有基础方法
def getBaseFunctions(path):

    base_modes_dict = {}
    functions = []
    ls_path = os.listdir(baseModeDataPath)
    files_path = [
        os.path.join(baseModeDataPath, _) for _ in ls_path if ls_path
    ]
    if files_path:
        for _ in files_path:
            functions += _readDataFile(_)

        for _ in functions:
            item_name = _['Parameter']
            if item_name in base_modes_dict.keys():
                base_modes_dict[item_name]['Functions'].append(_['Function'])
            else:
                item_dict = {
                    'Type': _['Type'],
                    'Description': _['Description'],
                    'Functions': [_['Function']]
                }
                base_modes_dict[item_name] = item_dict

    return base_modes_dict


class arg(argparse.ArgumentParser):
    def __init__(self, welcome=None):
        super().__init__()

        self.new_functions = []
        self.base_functions = []
        self.formatter_class = argparse.RawDescriptionHelpFormatter
        self.description = welcome
        self.add_argument("function", action="store", help="select function.")
        self.add_argument('-f', dest='file', help='selec exec file')
        self.add_argument('-u', dest='user', help='zabbix api user')
        self.add_argument('-p', dest='passwd', help='zabbix api password')
        self.add_argument('-a', dest='api', help='zabbix api url')
        self.add_argument(
            '--version', action='version', version='zabbixTools v1.0')


    def show_base_functions(self):
        base_modes_dict = getBaseFunctions(baseModeDataPath)
        for _ in base_modes_dict.keys(): 
            self.base_functions.append(_)
        for arg in base_modes_dict:
            item = base_modes_dict[arg]
            self.add_argument(
                "--%s" % arg,
                action='append',
                help="%s Can be used: (%s)" % (item['Description'], ','.join(
                    item['Functions'])))

    def all_args(self):
        d = vars(self.parse_args())
        for _ in list(d.keys()):
            if not d[_]:
                del d[_]
        return d

    def register_func(self, func, action="store"):
        args_list = getDoc2Dict(func)

        if args_list:
            for k,h in args_list.items():
                self.add_argument(
                    "--%s" % k,
                    action = action,
                    help = "from %s function , info:%s" % (func.__name__,h))
        return self.new_functions.append(func.__name__)
