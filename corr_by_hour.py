# -*- coding: utf-8 -*-
"""
corr by hour
"""

import pymysql
from sshtunnel import SSHTunnelForwarder
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def con_sshDb(sql):
    server = SSHTunnelForwarder(
            ('202.120.32.247', 54321),
			ssh_password="public",
			ssh_username="public",
			remote_bind_address=('127.0.0.1', 3306)
            )
    server.start()
    print (server.local_bind_port)
    conn = pymysql.connect(host='127.0.0.1', port=server.local_bind_port, user='public', passwd='public', db='data', charset='utf8mb4')
    data = pd.read_sql_query(sql, conn)
    conn.close()
    server.stop()
    return data

polution = ['PM25','SO2','o3','PM10','NO2','CO']
weather = ['rain','airpressure', 'temperature','humidity','windspeed']
other = ['date', 'time']

if __name__ == "__main__":
    for city in ['上海']:
        #city_info = con_sshDb('select * from wumai_app_city_info') #tbl = city_info, data_info, industry_info, 
        data = con_sshDb("SELECT * FROM wumai_app_data_info WHERE cityname = '"+city+"' HAVING date like '2018-12-%' ORDER BY date desc, time desc limit 24")
        data_filter = data[polution+weather].astype(float)
        corr = data_filter.corr()
        corr_filter = corr[polution].loc[weather]
        top = -np.sort(-corr_filter.values, axis=None)[:4]
        res = []
        for i in range(corr_filter.shape[0]):
            for j in range(corr_filter.shape[1]):
                if corr_filter.iat[i,j] in top:
                    res.append([corr_filter.iat[i,j], corr_filter.index.tolist()[i], corr_filter.columns.tolist()[j]])
        res = pd.DataFrame(res).sort_values(by=0, ascending=False)
        
        #-----------------------plot--------------------------------------------------------------
        xlabels = [x[5:7]+'-'+x[8:10]+' '+x[10:12]+'时' for x in (data['date']+data['time']).tolist()]
        xys = [[list(map(eval, data[res[1][i]].tolist())), list(map(eval, data[res[2][i]].tolist())), (res[1][i], res[2][i])] for i in range(4)]
        fig = plt.figure(figsize=(22,22))
        plt.rcParams['font.sans-serif']=['SimHei'] # chinese char
        plt.rcParams['axes.unicode_minus'] = False # minus char 
        for i in range(4):
            ax1 = fig.add_subplot(2,2,i+1)
            ax2 = ax1.twinx()
            ax1.plot(list(range(1,25)), xys[i][0], 'o-', c = 'b', label = xys[i][2][0])
            ax2.plot(list(range(1,25)), xys[i][1], 'o-', c = 'r', label = xys[i][2][1])
            ax1.legend(loc='left', fontsize=24)
            ax2.legend(loc='right', fontsize=24)
            ax1.set_xlabel('time'+'  corr='+str(res[0][i]), fontsize=22)
            ax1.set_xticks(range(0,24))
            ax1.set_xticklabels(xlabels)
            plt.setp(ax1.get_xticklabels(), rotation=90, ha='right', rotation_mode='anchor')
            ax1.set_ylabel(xys[i][2][0], fontsize=24)
            ax2.set_ylabel(xys[i][2][1], fontsize=24)
            ax1.tick_params(labelsize=16)
            ax2.tick_params(labelsize=16)
        fig.suptitle(city, x=0.45, y=1.0)
        fig.savefig(city+'_latest24_test.jpg', dpi=100)
        plt.show()
        fig.clear()