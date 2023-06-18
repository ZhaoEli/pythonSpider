import json
import random
import time
import requests
from lxml import etree
from fake_useragent import UserAgent
import xlwt
import csv
import ast
import pandas as pd

class courts(object):
    def __init__(self):
        self.filename= '法院备份.csv'
        #配置文件，存储要更新哪些省的数据
        self.inipath = "法院所在省份.ini"
        self.province_ct_url='https://splcgk.court.gov.cn/gzfwww//getFyLbBySf'
        self.second_ct_url='https://splcgk.court.gov.cn/gzfwww//getFyLbByXq'
        self.second_couts_path= '二级目录法院.csv'

        self.headers={'User-Agent':UserAgent().chrome
                      # 'Sec-Ch-Ua-Platform':"macOS",
                      # 'Cookie':'JSESSIONID=A9A52A48F3ACB741FB3D5BA7DFADB248; UM_distinctid=18886e2f1aa6eb-078463f64896e8-1b525634-13c680-18886e2f1abbb2; wzws_sessionid=oGR8pKWCZDg2YzYygDExNy4xNDcuMTE1LjY4gTVmMGZmNQ==; route=d712efb9298111eb12d28d5b4cf617e3',
                      # 'Accept-Language':'zh-CN,zh;q=0.9'
                      }

    def get_param(self,provinceid):
        params = {
            "sf": provinceid
        }
        return params
    def get_params(self,fyid,fymc):
        '''
        获取二级法院目录
        :param fyid: 法院id
        :param fymc: 法院名称
        :return: 字典
        '''
        params = {
            "fyid": fyid,
            'fymc': fymc
        }
        return params
    def post_response(self, url,params):
        '''
        获取法院列表
        :param province:
        :return: resonse.json()
        '''
        # 使用 reqeusts.post()方法提交请求

        try:
            response = requests.post(
                url=url,
                data=params,
                headers=self.headers
            )
        except Exception as e:
            print(e)
        else:
            # 通过status_code判断请求结果是否正确
            if response.status_code == 200:
                # print(response.text)
                # print(response.request.headers)
                # print(str(response.status_code), response.url)
                # print(response.text)
                return response
            else:
                print('请求错误：' + str(response.status_code) + ',' + str(response.reason))
    # def read_csv_data(self,path):

    def read_ini(self,path):
        '''
        获取要抓取的省份，从配置文件中读取
        path直接引用对象的path
        :return: 省份list
        '''
        f = open(path, encoding='utf-8')
        province=[]
        for line in f:
            province.append(line.strip('\n'))
        f.close()
        return province
    def write_csv(self,path,list):
        #追加写入
        with open(path,'a',newline='',encoding='utf-8') as f:
            w = csv.writer(f, delimiter=',')
            flag=0
            for j in list:
                l=[]
                l.append(j)
                w.writerow(l)
                flag+=1
            f.close()
            print('*****抓取了',flag,'条数据****')
    def get_second_courts(self):
        '''
        抓取二级所有法院数据
        s1：新建对象
        s2：运行主函数
        :return: 空
        '''
        try:
            with open(self.filename, encoding='utf-8') as f:
                for row in csv.reader(f):
                    # 读取的字符串转换为JSON对象
                    json = ast.literal_eval(row[0])
                    courtid=json['cgbm']
                    params=self.get_param(courtid)
                    # res=self.post_response(self.second_ct_url,params)
                    res = requests.post(
                        url=self.second_ct_url,
                        data=params,
                        headers=self.headers,
                     )

                    if res.text !='':
                        content=res.json()
                        self.write_csv(self.second_couts_path,content)
                    else:
                        print('当前代码{id}无法获取数据！'.format(id=courtid))
                    time.sleep(random.randint(2,4))
            f.close()
        except Exception as e:
            print(e)
    def write_all_courts(self):
        '''
        写入一级所有法院数据
        s1：新建对象
        s2：运行主函数
        :return: 空
        '''
        try:
            province_list=self.read_ini(self.inipath) #读取法院坐在的省区列表
            flag=0
            # print(province_list)
            #写数据


            #开始爬取数据
            for i in range(0,len(province_list)): #便利省区列表
                flag=0
                #写数据

                 #标记上一级id
                province=province_list[i]
                with open('./法院列表/'+province + '.csv', 'a', newline='', encoding='utf-8') as f:
                    w = csv.writer(f, delimiter=',')
                    flag +=1
                    print('现在正在采集省份：',province,'这是第',flag,'个省份！')
                    params=self.get_param(province)
                    list=self.post_response(
                        url=self.province_ct_url,
                        params=params).json()
                    # heads=[].append(list[0].keys) #获取表头
                    for j in list:
                        upper_dict_flag = {'upper_cgbm': ''}
                        j.update(upper_dict_flag)
                        list_temp=[]
                        list_temp.append(j)
                        w.writerow(list_temp)
                        #***********
                        # 获取二级法院名单
                        # print(len(list))
                        courtid = j['cgbm']
                        params = self.get_param(courtid)
                        res = requests.post(
                            url=self.second_ct_url,
                            data=params,
                            headers=self.headers,
                        )
                        if res.text =='':
                            #如果无返回则直接跳出当前循环
                            continue
                            print('当前代码{id}无法获取数据！'.format(id=courtid))

                        else:
                            upper_dict_flag.update({'upper_cgbm': courtid})  # 增加上一级字段，并标记ID
                            content = res.json()
                            count_numbers =0
                            for p in content:
                                if j['cname'] ==p['cname']:continue #避免写入重复数据
                                p.update(upper_dict_flag)
                                list_temp=[]
                                list_temp.append(p)
                                w.writerow(list_temp)
                                count_numbers += 1
                                time.sleep(random.randint(1, 2))
                            print("*******获取了",count_numbers,"条子数据！")
                        #子法院抓取完成，进行下一个
                        time.sleep(random.randint(1,2))
                    f.close()
        except Exception as e:
            print(e)




if __name__ == '__main__':
    spider=courts()
    spider.write_all_courts()

