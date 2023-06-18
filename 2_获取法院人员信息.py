import csv
import re
import random
import time
import ast
import requests
from fake_useragent import UserAgent

class get_Judgers(object):
    def __init__(self):
        self.api='https://splcgk.court.gov.cn/gzfwww///fgmlList' #获取列表
        self.headers={
            'User-Agent':UserAgent().chrome
        }
    def get_args(self,fyid,fymc):
        '''
        post传参数
        :param fyid: 法院id
        :param fymc: 法院名称
        :return: json args params
        '''
        args={
            'fyid': fyid,
            'fymc': fymc
        }
        return args

    def get_courts_files(self,path):
        '''
        获取法院列表
        :param path:
        :return:dict
        '''
        temp_dic = {}
        f = open(path, 'r',newline='', encoding='utf-8')
        for line in f:
            j = ast.literal_eval(eval(line))
            temp_dic.update({j['cname']:j['cid']})
        f.close()
        return temp_dic

    def run(self,read_path,write_path):
        #读取法院数据
        courts_dict=self.get_courts_files(read_path)
        with open(write_path, 'a', newline='', encoding='utf-8') as p:
            w=csv.writer(p, delimiter=',')
            '''
            获取表头
            '''
            # 遍历法院
            for key, value in courts_dict.items():
                counts=0
                print(key)

                args = self.get_args(fyid=value, fymc=key)
                res = requests.post(
                    url=self.api,
                    data=args,
                    headers=self.headers,
                )
            # fymc='浙江省高级人民法院'
            # fyid='A4E2B7B5AB011BC14F8963FA38519F21'
            # args=self.get_args(fyid=fyid,fymc=fymc)
            # res=requests.post(
            #     url=self.api,
            #     data=args,
            #     headers=self.headers,
            # )
                content=res.text
                pattern= re.compile('</td>.*?>(.*?)</td>'
                                    '.*?>(.*?)</td>.*?>(.*?)</td>.*?>(.*?)</td>.*?>(.*?)</td>.*?</tr>', re.S)
                list=pattern.findall(content)
                if len(list)==0:
                    continue
                for j in list:
                    l=[key,value]
                    for i in range(0,len(j)):
                        l.append(j[i])
                    w.writerow(l)
                    counts+=1
                print('——————',key,'采集了',counts,'人—————————')
                time.sleep(random.randint(1,3))
            p.close()



if __name__ == '__main__':
    spider=get_Judgers()

    with open('法院所在省份.ini','r', newline='', encoding='utf-8') as f:
        for p in f:
            province=p.strip('\n')
            if province=='北京' or province=='天津':continue
            read_path = './1、法院列表/'+province+'.csv'
            write_path = './2、法官列表/'+province+'.csv'
            spider.run(read_path=read_path, write_path=write_path)
            time.sleep(random.randint(1,2))
    f.close()
