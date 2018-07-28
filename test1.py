# -*- coding:utf-8 -*- 
'''
Created on 2017/10/14
@author: Joy Hou
'''
import tushare as ts
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import traceback

from functools import wraps
import sys

import openpyxl
from openpyxl.styles import Font, Color
from openpyxl.styles import colors, PatternFill


def singleton(cls):
    instances = {}

    @wraps(cls)
    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
            return instances
        return instances

#@singleton
class Stocks(object):
    instance = None

    def __init__(self):
        self.allStocks = None
        self.codes = []
# 用print(Stock.GetInstance) 查看是否绑定
    @classmethod
    def GetInstance(cls):
        if cls.instance == None:
            cls.instance = Stocks()
        return cls.instance
    # 外部函数 和 该类无关系 不进行绑定
    @staticmethod
    def GetInstance1():
        if Stocks.instance == None:
            Stocks.instance = Stocks()
        return Stocks.instance

    def __check(self):
        for i in self.__stocks.index:
            nt = self.__stocks.loc[i].values[self.__getIdx('name')]
            for c in nt:
                if c == ' ':
                    #print('包含有空格:', nt)
                    nt = nt.replace(' ','')
                    self.__stocks.loc[i, 'name'] = nt# .values[self.__getIdx('name')] = nt
                    #nt = self.__stocks.loc[i].values[self.__getIdx('name')] 
                    #print('包含有空格:', nt)
                    break

    def GetStocks(self):
        if type(self.allStocks) == type(None):
            self. allStocks = ts.get_stock_basics()
            self.__check()

        return self.allStocks

    @property
    def __stocks(self):
        return self.GetStocks()

    def __getCols(self):
        return self.__stocks.columns.values.tolist()

    def __getIdx(self, name):
        cols = self.__getCols()
        return cols.index(name)

## public
    def GetCode(self, name):
        lcode = [] 
        for i in self.__stocks.index:
            nt = self.__stocks.loc[i].values[self.__getIdx('name')]
            if  name == nt:
                c = i #self.__stocks.loc[i].values[self.__getIdx('code')]
                lcode.append(c)
        return lcode

    def GetCodes(self):
        if len(self.codes) == 0:
            for i in self.__stocks.index:
                self.codes.append(i)
        return self.codes

    def GetName(self, code):
        return self.__stocks.loc[code, 'name']

    def GetStock(self, code):
        name = self.__stocks.loc[code, 'name']
        industry  = self.__stocks.loc[code, 'industry']
        pe = self.__stocks.loc[code, 'pe']
        outstanding = self.__stocks.loc[code, 'outstanding']
        total = self.__stocks.loc[code, 'totals']
        per = float(outstanding)/total
        s = StockSimple(code, name, industry, pe, outstanding, total, per)
        return s

    def PrintInfo(self, code):
        name = self.__stocks.loc[code, 'name']
        industry  = self.__stocks.loc[code, 'industry']
        pe = self.__stocks.loc[code, 'pe']
        outstanding = self.__stocks.loc[code, 'outstanding']
        total = self.__stocks.loc[code, 'totals']
        per = float(outstanding)/total
        print (name, " ", industry,"市盈:", pe, " 流通:", outstanding, " 总股本:", total, " 流通占比:", per)

class Util(object):
    def WriteToxlsx(self, fileName="", objs=[]):
        wb = openpyxl.Workbook()
        wb.create_sheet("xx")
        ws = wb.active
        cols = ['代码', '名字', '行业', '市盈', '流通', '总股本', '流通占比']
        i = 0
        for col in cols:
            i += 1
            ws.cell(column = i, row=1, value=col)
        r = 2
        for obj in objs:
            for col in cols:
                ws.cell(r, cols.index(col) + 1, value = obj.GetValue(col))
            r += 1
        wb.save(fileName)

class StockSimple(object):
    def __init__(self, code = "", name = "", industry="", pe="", outstanding="", total="", per=0.0):
        self.code = code
        self.name = name
        self.industry = industry
        self.pe = pe
        self.outstanding = outstanding
        self.total = total
        self.per = per

    def GetValue(self, alias):
        if alias == '代码':
            return self.code
        if alias == '名字':
            return self.name
        if alias == '行业':
            return self.industry
        if alias == '市盈':
            return self.pe
        if alias == '流通':
            return self.outstanding
        if alias == '总股本':
            return self.totals
        if alias == '流通占比':
            return self.per


    @property
    def Code(self):
        return self.code
    @property
    def CirRate(self):
        return str(self.per*100)+'%%'

class Algorithm(object):

    def __get_oldtime(self, time1, interval):
        inter_time = interval*24*3600
        old_time = time.strftime('%Y-%m-%d',time.localtime(time1-inter_time))
        return old_time

    # 长时间横盘 突然上涨的股票
#
#获取当前日期算起Ｎ日的收盘价
#
    def HengUp(self, weight=30, updot=4, curupdot=2):
        upDotRate = updot/100.0
        curUpDotRate = curupdot/100.0
        stocks = Stocks.GetInstance()
        codes = stocks.GetCodes()
        old_day = self.__get_oldtime(time.time(), weight)
        today=time.strftime('%Y-%m-%d',time.localtime(time.time()))
        li = []

        for v in codes:
            data = ts.get_hist_data(v, start=old_day, end=today, ktype='D')
            #print(data)
            try:
                if type(data) == type(None) or type(data['close']) == type(None):
                    continue
                count = len(data['close'])
                if count > weight/2:
                    begin = data['close'][count - 1]
                    valid_count = 0
                    avalid_count = 0
                    #for vv in data['close']:
                    for n in range(count-1, -1, -1):
                        prePrice = data['close'][n]
                        #print v, code_name_dic[v], vv, "n:", n, "count:", count, "valid:", valid_count
                        if n != 0:
                            if abs(prePrice-begin) < upDotRate*begin:
                                valid_count += 1
                            else:
                                if avalid_count > 3:
                                    break
                                avalid_count += 1
                        else:
                            cur = data['close'][0] 
                            sec = data['close'][1] 
                            if cur > sec:
                                if cur - sec > curUpDotRate*sec:
                                    valid_count += 1
                    #print "有效个数:", valid_count, " 无效个数:", avalid_count," 总数:", count                
                    if valid_count >= count-avalid_count:
                        name = stocks.GetName(v)
                        print (v, name, '开始价格', begin, '持续天数:', valid_count)
                        stocks.PrintInfo(v)
                        
                        tup = (v, data)
                        li.append(tup)

            except Exception as e:
                msg = traceback.format_exc()
                print(msg)
                #print ('异常', e)
        return li        

alg = Algorithm()
li = alg.HengUp(weight=15, updot=4, curupdot=2)
# (code, data)

stocks = Stocks.GetInstance()
ls = []
for tup in li:
    code = tup[0]
    sobj = stocks.GetStock(code)
    ls.append(sobj)
    #stocks.PrintInfo(code)
    #tup[1]['close'].plot()
    #plt.show()

ls.sort(key=lambda obj: obj.pe, reverse=False)    
print("sort:")
print("write to xlsx")
util = Util() 
util.WriteToxlsx(fileName="xxx.xlsx", objs=ls)
for s in ls:
    stocks.PrintInfo(s.Code)
