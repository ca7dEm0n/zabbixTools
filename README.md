# zabbixTools

Zabbix`API`命令行工具

> 依赖`Data`目录下的数据文件，因为懒得写爬虫，用excle处理也行.

```
# 格式
groupids	|	string/array	|	Return only hosts that belong to the given groups.

# 对应官网API文档列表，自行参照API
# https://www.zabbix.com/documentation/3.4/manual/api
```

**功能**
- 支持命令行下一些简单的`zabbix`操作.
- 支持读取`excel`文件批量操作.
- 便于其他框架引入.

### 简单使用


**授权**
授权方式两种：
- 命令行
	`-u` 指定登录用户名.
	`-p` 指定登录用户密码.
	`-a` 指定`api`地址.
	
- 配置文件.

**使用**
以获取`host`为例：
> 官网示例：https://www.zabbix.com/documentation/3.2/manual/api/reference/host/get
```
{
    "jsonrpc": "2.0",
    "method": "host.get",
    "params": {
        "filter": {
            "host": [
                "Zabbix server",
                "Linux server"
            ]
        }
    },
    "auth": "038e1d7b1735c6a5436ee9eae095879e",
    "id": 1
}
```
对应工具的操作：
```
> python zabbixTools.py host.get --filter host --host 'Zabbix server,10.0.0.1'

# 返回
[{'hostid': '10136', 'proxy_hostid': '0', 'host': '10.0.0.1', 'status': '0', 'disable_until': '0', 'error': '', 'available': '1', 'errors_from': '0', 'lastaccess': '0', 'ipmi_authtype': '-1', 'ipmi_privilege': '2', 'ipmi_username': '', 'ipmi_password': '', 'ipmi_disable_until': '0', 'ipmi_available': '0', 'snmp_disable_until': '0', 'snmp_available': '0', 'maintenanceid': '0', 'maintenance_status': '0', 'maintenance_type': '0', 'maintenance_from': '0', 'ipmi_errors_from': '0', 'snmp_errors_from': '0', 'ipmi_error': '', 'snmp_error': '', 'jmx_disable_until': '0', 'jmx_available': '0', 'jmx_errors_from': '0', 'jmx_error': '', 'name': '192.168.8.39', 'flags': '0', 'templateid': '0', 'description': '', 'tls_connect': '1', 'tls_accept': '1', 'tls_issuer': '', 'tls_subject': '', 'tls_psk_identity': '', 'tls_psk': ''}, {'hostid': '10084', 'proxy_hostid': '0', 'host': 'Zabbix server', 'status': '0', 'disable_until': '0', 'error': '', 'available': '1', 'errors_from': '0', 'lastaccess': '0', 'ipmi_authtype': '-1', 'ipmi_privilege': '2', 'ipmi_username': '', 'ipmi_password': '', 'ipmi_disable_until': '0', 'ipmi_available': '0', 'snmp_disable_until': '0', 'snmp_available': '0', 'maintenanceid': '0', 'maintenance_status': '0', 'maintenance_type': '0', 'maintenance_from': '0', 'ipmi_errors_from': '0', 'snmp_errors_from': '0', 'ipmi_error': '', 'snmp_error': '', 'jmx_disable_until': '0', 'jmx_available': '0', 'jmx_errors_from': '0', 'jmx_error': '', 'name': 'Zabbix server', 'flags': '0', 'templateid': '0', 'description': '', 'tls_connect': '1', 'tls_accept': '1', 'tls_issuer': '', 'tls_subject': '', 'tls_psk_identity': '', 'tls_psk': ''}]
```

**其他方法支持**
	在`Data`目录下新增以方法名命名的数据文件.

**自定义开发**

> 在面对一些复杂的应用场景，非常多的参数以及繁琐步骤会令你痛苦不堪，可选择自定义开发

效果演示

> 以快速创建`HTTP站点监控`为例（见：`demo.py`）
```
> python demo.py  createHttp  --name "asd" --step_no 1 --step_url "www.baidu.com" --step_name "asd"

{'hostid': '10254', 'name': 'asd', 'agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36', 'delay': '60', 'status': '0', 'applicationid': '1058', 'steps': [{'name': 'asd', 'no': '1', 'url': 'www.baidu.com', 'follow_redirects': '0', 'timeout': '60'}]}
```


> 自用脚本，较为简单草率，欢迎各路大神指点，万分感激！