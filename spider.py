# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 11:50:02 2019

@author: mzwei
"""

import urllib.request
from bs4 import BeautifulSoup
import pandas as pd   
import re

def coding(url):
    return urllib.request.quote(url, safe=';/?:@&=+$,', encoding='utf-8')

def get_baike_url(wd):
    url = coding('https://www.baidu.com/s?wd='+wd)
    req = urllib.request.Request(url)
    req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36')
    html = urllib.request.urlopen(req).read()
    urls = BeautifulSoup(html).select('.result-op.c-container.xpath-log')
    return coding(urls[0].attrs['mu'])
    
res = []
provinces = ['贵州', '四川', '北京', '甘肃', '内蒙古', '吉林', '西藏', '新疆', '广东', '宁夏', '山西', '陕西', '福建', '湖南', '湖北', '广西', '江苏', '浙江', '上海', '天津', '重庆', '黑龙江','青海', '海南', '江西', '山东', '辽宁', '云南', '安徽', '河南', '河北']
for p in provinces:
    url = get_baike_url(p)
    print (p, url)
    req = urllib.request.Request(url)
    req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36')
    html = urllib.request.urlopen(req).read()
    
    soup = BeautifulSoup(html)
    k = soup.select('.basicInfo-item.name')
    v = soup.select('.basicInfo-item.value')
    s = soup.select('.lemma-summary')
    
    k = [x.get_text() for x in k] + ['百度百科']
    s = re.sub('[\n\xa0]', '', s[0].get_text())
    v = [re.match('\n(.*)\n.*', x.get_text()).group(1) for x in v] + [s]
    
    df = pd.DataFrame([v], columns=k)
    res.append(df)
    

merge_res = res[0]
for df in res[1:]:
    merge_res = pd.concat([merge_res, df])
merge_res.to_csv('province_info.csv', encoding='utf_8_sig')


