from args import arg
from zabbix import Zabbix

zabbix = Zabbix()

"""
 自定义方法


1. 使用zabbix.get(post_dict)完成API请求
    - post_dict为字典类型
    - post_dict需包含'function'

2. 使用arg.register_func方法对自定义方法进行注册
    - 默认会读取注册方法的注释文档，生成帮助文档
    - 以冒号区分开，左边为参数，右边为注释
    - 自定义方法第一个参数传入zabbix,第二个参数为post_dict

3. 可以新增读取excel批量操作，具体方法见zabbixTools.py

4. 需要Post的数据见官网

"""



def createHttp(z, post_dict=None):
    """
    host: 部署到该服务器,默认Zabbix server
    template_name: 模板名,默认TestTemplate
    application: 应用集, 默认TestApplication
    step_name: 场景名称,必填
    step_no: 场景ID,默认为1
    step_url: 场景链接,必填
    step_headers: 场景请求头，默认为空
    follow_redirects: 是否跟随跳转，默认不跟随跳转
    headers: 场景请求头，默认为空
    posts: POST内容,默认为空
    required: 场景正常的字符串,默认为空
    timeout: 超时时间,默认60秒
    step_variables: 场景变量,默认为空
    status_codes: 场景正常的状态码,默认200
    name: HTTP名称,必填
    agent: HTTP请求头,默认为谷歌
    delay: 间隔时间,默认60秒
    retries: 失败尝试,默认为空
    status: HTTP开启状态,默认为开启
    variables: HTTP变量,默认为空
    """
    host = post_dict.get('Host', 'Zabbix server')
    template_name = post_dict.get('TemplateName', 'TestTemplate')
    application_name = post_dict.get('Application', 'TestApplication')

    hostid = z.get(host_get_dict(host))[0]['hostid']
    template = z.get(template_get_dict(template_name))
    if not template:
        print('not find template , create now')
        templateid = z.get(template_create_dict(template_name,
                                                hostid))['templateids'][0]
    else:
        templateid = template[0]['templateid']

    application = z.get(application_get_dict(templateid))
    if not application:
        print('not find application , create now')
        applicationid = z.get(
            application_create_dict(application_name,
                                    templateid))['applicationids'][0]
    else:
        applicationid = application[0]['applicationid']

    httptext = z.get(httptest_get_dict(hostid))
    http_list = {}
    if httptext:
        for _ in httptext:
            http_list[_['name']] = _['httptestid']
    if post_dict['name'] not in http_list.keys():
        postDict = httptest_create_dict(templateid, applicationid, post_dict)
        http_id = z.get(postDict)
        print(http_id)
    print(httptext)


def httptest_create_dict(hostid, applicationid, post_dict):
    step_dict = {
        'name': post_dict.get('step_name', ''),
        'no': post_dict.get('step_no', '1'),
        'url': post_dict.get('step_url', ''),
        'follow_redirects': post_dict.get('step_follow_redirects', '0'),
        'headers': post_dict.get('step_headers', ''),
        'posts': post_dict.get('posts', ''),
        'required': post_dict.get('required', ''),
        'timeout': post_dict.get('timeout', '60'),
        'variables': post_dict.get('step_variables', ''),
        'status_codes': post_dict.get('status_codes', '')
    }

    for _ in list(step_dict):
        if not step_dict[_]:
            del step_dict[_]

    http_dict = {
        'function':
        'httptest.create',
        'hostid':
        hostid,
        'name':
        post_dict.get('name', ''),
        'agent':
        post_dict.get(
            'agent',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36'
        ),
        'delay':
        post_dict.get('delay', '60'),
        'retries':
        post_dict.get('retries', ''),
        'headers':
        post_dict.get('headers', ''),
        'status':
        post_dict.get('status', '0'),
        'applicationid':
        applicationid,
        'variables':
        post_dict.get('variables', ''),
        'steps': [step_dict],
        'templateid':
        post_dict.get('templateid', '')
    }

    for _ in list(http_dict):
        if not http_dict[_]:
            del http_dict[_]
    return http_dict


def httptest_get_dict(hostid):
    return {'function': 'httptest.get', 'hostid': hostid}


def template_get_dict(templename):
    return {'function': 'template.get', 'filter': {'host': [templename]}}


def template_create_dict(templename, hostid):
    return {
        'function': 'template.create',
        'host': templename,
        'groups': {
            'groupid': 1
        },
        'hosts': [{
            "hostid": hostid
        }]
    }


def host_get_dict(host):
    return {'function': 'host.get', 'filter': {'host': host}}


def application_get_dict(templateid):
    return {'function': 'application.get', 'hostids': templateid}


def application_create_dict(name, hostid):
    return {'function': 'application.create', 'name': name, 'hostid': hostid}


if __name__ == "__main__":
    a = arg('hello')
    # 注册自定义方法
    a.register_func(createHttp)

    # 获取命令行所有参数
    post_dict = a.all_args()

    # zabbix登录操作
    zabbix.login(post_dict)
    function = str(post_dict['function'])

    if function in a.new_functions:
        globals()[function](zabbix, post_dict)
