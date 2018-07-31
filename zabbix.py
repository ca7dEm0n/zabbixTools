# -*- coding: utf-8 -*-

import json
import requests
import os
rootPath = os.path.abspath(os.path.dirname(__file__))


class Zabbix:
    def __init__(self):
        self.myRequests = requests.Session()
        self.AUTH = None
        self.USER = None
        self.PASSWD = None
        self.API = None

    def post(self, Data):
        JsonHeader = {'Content-Type': 'application/json-rpc'}
        res = self.myRequests.post(url=self.API, data=Data, headers=JsonHeader)
        return res.json()

    def get(self, post_dict):
        @self.base(post_dict['function'])
        def _exe(d):
            return d
        del post_dict['function']
        return _exe(post_dict)

    def login(self, post_dict):
        import time, configparser
        config = configparser.ConfigParser()
        tmp_file = os.path.join(rootPath, 'zbx_temp')

        if os.path.exists(tmp_file):
            now_time = int(time.time())
            file_mtime = int(os.path.getmtime(tmp_file))
            if now_time - file_mtime <= 10:
                with open(tmp_file, 'r') as f:
                    login_dict = json.loads(f.read().rstrip())
                self.AUTH = login_dict['auth']
                self.API  = login_dict['api']
                return self.AUTH

        @self.base('user.login')
        def _get_auth(user, passwd):
            return {"user": user, "password": passwd}

        configPath = os.path.join(rootPath, 'zabbixTools.conf')

        if os.path.exists(configPath):
            config.read(configPath)

            self.USER = post_dict.get("user", "") or config.get(
                'zabbix', 'user', fallback=0)

            self.PASSWD = post_dict.get("passwd", "") or config.get(
                'zabbix', 'passwd', fallback=0)

            self.API = post_dict.get("api", "") or config.get(
                'zabbix', 'api', fallback=0)

        LOGIN_DICT = {
            "user": self.USER,
            "passwd": self.PASSWD,
            "api": self.API
        }

        for _ in LOGIN_DICT:
            if not LOGIN_DICT[_]:
                return "%s is miss" % _

        auth = _get_auth(self.USER, self.PASSWD)
        if not isinstance(auth, dict):
            with open(tmp_file, 'w') as f:
                LOGIN_DICT['auth'] = auth
                json.dump(LOGIN_DICT,f)
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
        # 如果传入的参数中有带'params' 直接返回
        if "params" in post_dict.keys():
            postData = post_dict['params'].split(',')
            response = self.get(postData)
            return response

        # 进行转换，除了包含'['外，其余出现逗号转为列表对象
        for _ in post_dict.keys():
            if isinstance(post_dict[_], list) and len(post_dict[_]) == 1:
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
                        new_list = value2Array(post_dict, _)
                        post_dict[_] = new_list

        for i in del_key_list:
            if i in post_dict.keys():
                del post_dict[i]

        response = self.get(post_dict)
        return response


def _str2List(text):
    """
    包含逗号的文本进行转换
    """

    if isinstance(text, list):
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
        k_list = d[k] if isinstance(d[k], list) else d[k].split(',')
        for i in k_list:
            d[k] = {}
            d[k][i] = _str2List(d[i])
            del d[i]


def value2Array(d, k):
    """
    将外面的参数放进字典,针对object/array对象
    """

    if d.get(k, ''):
        k_list = d[k] if isinstance(d[k], list) else d[k].split(',')
        len_max = max([len(d[_]) for _ in k_list if _ in d.keys()])
        new_list = []
        for _ in range(0, len_max):
            i_dict = {i: "" for i in k_list if k_list}
            for k in k_list:
                if len(d[k]) > _:
                    i_dict[k] = d[k][_]
                else:
                    del i_dict[k]

            new_list.append(i_dict)
        return new_list


if __name__ == "__main__":
    zabbix = Zabbix()

    a = zabbix.login({'user': 'Admin', 'passwd': 'zabbix'})
    print(a)
