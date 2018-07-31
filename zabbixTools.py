# -*- coding: utf-8 -*-
from args import arg
from zabbix import Zabbix
from readExcel import readExcel
zabbix = Zabbix()


if __name__ == '__main__':

    a = arg('hello')
    post_dict = a.all_args()
    zabbix.login(post_dict)
    function = str(post_dict['function'])

    if post_dict.get('file',None):
        excelDataList = readExcel(post_dict['file'])
        if function in a.base_functions:
            for _ in excelDataList:
                print (zabbix.baseFunction(_))
                
        if function in a.new_functions:
            for _ in excelDataList:
                globals()[function](zabbix,_)
    else:
        print (zabbix.baseFunction(post_dict))
