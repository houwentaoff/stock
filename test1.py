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

today=time.strftime('%Y-%m-%d',time.localtime(time.time()))

def get_oldtime(time1, interval):
    inter_time = interval*24*3600
    old_time = time.strftime('%Y-%m-%d',time.localtime(time1-inter_time))
    return old_time

allstocks = ts.get_stock_basics()

def prt_stock_info(code):
    name = allstocks.loc[code, ['name']]
    industry  = allstocks.loc[code, ['industry']]
    pe = allstocks.loc[code, ['pe']]
    outstanding = allstocks.loc[code, ['outstanding']]
    total = allstocks.loc[code, ['totals']]
    per = float(outstanding)/total
    print name, " ", industry,"市盈:", pe, " 流通:", outstanding, " 总股本:", total, " 流通占比:", per
    
'''
获取当前日期算起Ｎ日的收盘价
'''
def get_all_stock_code():
    dic={}#'code':codes,'name':names}

    for item in allstocks.index:
        dic[item]=allstocks.loc[item, ['name']]
    return dic

old_day = get_oldtime(time.time(), 60)
print old_day,"--", today
code_name_dic = get_all_stock_code()

li=[]
for v in code_name_dic.keys():
    data = ts.get_hist_data(v, start=old_day, end=today, ktype='D')
    try:
        count = len(data['close'])
        if count > 30:
            begin = data['close'][count - 1]
            valid_count = 0
            avalid_count = 0
            #for vv in data['close']:
            for n in range(count-1, -1, -1):
                vv = data['close'][n]
                #print v, code_name_dic[v], vv, "n:", n, "count:", count, "valid:", valid_count
                if n != 0:
                    if abs(vv-begin) < 0.04*begin:
                        valid_count += 1
                    else:
                        if avalid_count > 3:
                            break
                        avalid_count += 1
                else:
                    a = data['close'][0] 
                    b = data['close'][1] 
                    if a > b:
                        if a - b > 0.02*b:
                            valid_count += 1
            #print "有效个数:", valid_count, " 无效个数:", avalid_count," 总数:", count                
            if valid_count >= count-avalid_count:
                prt_stock_info(v)
                print v,'开始价格', begin, '持续天数:', valid_count
                
                tup = (v,data)
                li.append(tup)

    except Exception as e:
        print '异常', e
for tup in li:
    prt_stock_info(tup[0])
#    print tup[0], code_name_dic[tup[0]]
    tup[1]['close'].plot()
    plt.show()
#a = ts.get_hist_data('600016')
#print allstocks.dtypes
