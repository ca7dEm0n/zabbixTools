# -*- coding: utf-8 -*-
import xlrd
import collections
def readExcel(filename):
    data = xlrd.open_workbook(filename)
    table = data.sheets()[0]
    nrows = table.nrows
    ncols = table.ncols
    dataList = []
    d = collections.OrderedDict()
    for x in range(nrows):
        if x == 0 :
            continue
        for y in range(ncols):
            if table.cell_value(x,y):
                d[table.cell_value(0,y)] = table.cell_value(x,y)
        dataList.append(d)
        d = collections.OrderedDict()
    return  dataList
