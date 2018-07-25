# -*- coding: utf-8 -*-
import sys
import os
import json
import argparse
import requests

rootPath = os.path.abspath(os.path.dirname(__file__))
configPath = os.path.join(rootPath, 'zabbixTools.conf')
baseModeDataPath = os.path.join(rootPath, 'Data')


class Zabbix:
    def __init__(self):
        self.myRequests = requests.Session()
        self.AUTH = None
        self.URL = None

    def post(self, Data):
        JsonHeader = {'Content-Type': 'application/json-rpc'}
        res = self.myRequests.post(url=self.URL, data=Data, headers=JsonHeader)
        return res.json()

    def login(self, post_dict):
        import time
        tmp_file = os.path.join(rootPath, 'zbx_temp')

        if os.path.exists(tmp_file):
            now_time = int(time.time())
            file_mtime = int(os.path.getmtime(tmp_file))
            if now_time - file_mtime <= 10:
                with open(tmp_file, 'r') as f:
                    auth = f.read().rstrip()
                self.AUTH = auth
                return auth

        @self.base('user.login')
        def _get_auth(user, passwd):
            return {"user": user, "password": passwd}

        user = post_dict.get('user', None)
        passwd = post_dict.get('password', None)
        auth = _get_auth(user, passwd)
        if not isinstance(auth, dict):
            with open(tmp_file, 'w') as f:
                f.write(auth)
            self.AUTH = auth
            return self.AUTH
        print("[!] Error Login")

    def base(self, method):
        def _Data(data):
            def _Dict(*args, **kw):
                D = {
                    "jsonrpc": "2.0",
                    "method": method,
                    "params": data(*args, **kw),
                    "id": 1,
                }
                if 'apiinfo.version' not in method:
                    D['auth'] = self.AUTH
                Dict = json.dumps(D)
                Post = self.post(Dict)
                if 'error' in Post:
                    return Post['error']
                return Post['result']

            return _Dict

        return _Data

    def baseFunction(self, post_dict, functions=None):
        @self.base(post_dict['function'])
        def _exe(d):
            return d

        # 如果传入的参数中有带'params' 直接返回
        if "params" in post_dict.keys():
            postData = post_dict['params'].split(',')

        # 进行转换，除了包含'['外，其余出现逗号转为列表对象
        for _ in post_dict.keys():
            if isinstance(post_dict[_],list) and len(post_dict[_]) == 1:
                if "[" not in post_dict[_]:
                    post_dict[_] = _str2List(post_dict[_])


        del_key_list = []
        # 对传进来的字典进行扫描  
        if functions:
            for _ in list(post_dict.keys()):
                if _ in functions.keys():
                    
                    # 如果是object对象,则把该值的参数组合成字典
                    if functions[_]['Type'] == "object":
                        value2Dict(post_dict, _)

                    # 如果是object/array对象,则...
                    if functions[_]['Type'] == "object/array":
                        for x in post_dict[_]:
                            del_key_list.append(x)
                        new_list = value2Array(post_dict,_)
                        post_dict[_] = new_list

        for i in del_key_list:
           if i in post_dict.keys():
               del post_dict[i]

        response = _exe(post_dict)
        return response


def _str2List(text):
    """
    包含逗号的文本进行转换
    """

    if isinstance(text,list):
        if ',' in text[0]:
            text = text[0].split(',')
        return text
    text = text.split(',') if ',' in text else text
    return text


def value2Dict(d, k):
    """
    将外面的参数放进字典,针对object对象
    """
    if d.get(k, ''):
        k_list = d[k] if isinstance(d[k],list) else d[k].split(',')
        for i in k_list:
            d[k] = {}
            d[k][i] = _str2List(d[i])
            del d[i]

def value2Array(d, k):
    """
    将外面的参数放进字典,针对object/array对象
    """

    if d.get(k,''):
        k_list  = d[k] if isinstance(d[k],list) else d[k].split(',')
        len_max = max([ len(d[_]) for _ in k_list if _ in d.keys()])
        new_list = []
        for _ in range(0,len_max):
            i_dict = { i:"" for i in k_list if k_list}
            for k in k_list:
                if len(d[k]) > _:
                    i_dict[k] = d[k][_]
                else:
                    del i_dict[k]

            new_list.append(i_dict)
        return new_list


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


if __name__ == '__main__':
    # 获取所有基础方法列表
    base_modes_list = os.listdir(baseModeDataPath)
    # 获取所有基础方法字典
    base_modes_dict = getBaseFunctions(baseModeDataPath)

    # 构建菜单栏
    # 初始化选项
    welcome = """
    BASE MODE FUNCTION
    ------------------
        %s

    """ % ('\t'.join(
        list(set(["\t%s\n" % _ for _ in os.listdir(baseModeDataPath)]))))
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=welcome)
    parser.add_argument("function", action="store", help="select function.")
    parser.add_argument('-f', dest='file', help='selec exec file')
    parser.add_argument('-u', dest='user', help='zabbix api user')
    parser.add_argument('-p', dest='passwd', help='zabbix api password')
    parser.add_argument('-a', dest='api', help='zabbix api url')
    parser.add_argument(
        '--version', action='version', version='zabbixTools v1.0')

    # 生成可选项帮助菜单
    for arg in base_modes_dict:
        item = base_modes_dict[arg]
        parser.add_argument(
            "--%s" % arg,
            action='append',
            help="%s Can be used: (%s)" % (item['Description'], ','.join(
                item['Functions'])))
    args = parser.parse_args()

    # 初始化Zabbix
    zabbix = Zabbix()
    c_zbx_user = c_zbx_pass = c_zbx_api = ""
    if os.path.exists(configPath):
        import configparser
        config = configparser.ConfigParser()
        config.read(configPath)

        c_zbx_user = config.get('zabbix', 'user', fallback=0)
        c_zbx_pass = config.get('zabbix', 'passwd', fallback=0)
        c_zbx_api = config.get('zabbix', 'api', fallback=0)

    # 登录所需信息
    ZBX_USER = args.user or c_zbx_user
    ZBX_PASS = args.passwd or c_zbx_pass
    ZBX_API = args.api or c_zbx_api
    LOGIN_DICT = {"user": ZBX_USER, "password": ZBX_PASS, "api": ZBX_API}
    for c in LOGIN_DICT:
        if not LOGIN_DICT[c]:
            print("please input :%s value " % c)

    # 选择模式
    if args.function in base_modes_list:
        zabbix.URL = ZBX_API
        zabbix.login(LOGIN_DICT)
        # 获取所有参数
        arg_dict = vars(parser.parse_args())

        # 删除为空的参数值
        for _ in list(arg_dict.keys()):
            if arg_dict[_] == None or arg_dict[_] == "":
                del arg_dict[_]

        # 发射
        fun_ex = zabbix.baseFunction(arg_dict, base_modes_dict)

        print(fun_ex)
