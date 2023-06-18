import csv
import re
import random
import time
import ast
import requests
from urllib import request
from configparser import ConfigParser   # Python2中是from ConfigParser import ConfigParser

from fake_useragent import UserAgent

class CasesSpider(object):
    def __init__(self):
        self.headers = {
          # 将拷贝的cookie值放在此处
          'Cookie':'UM_distinctid=18886e2f1aa6eb-078463f64896e8-1b525634-13c680-18886e2f1abbb2; HM4hUBT0dDOn443S=hHandc40IDs2R6t7vEKyQ3RuP6WW_yiZspDuVviypZM.LG5qcmX8ML_J0RBLZbAu; wzws_sessionid=gjZmNjkwMYE1ZjBmZjWAMTE3LjE0Ny4zMS4yMjOgZILguA==; SESSION=725aab06-5ec5-43a0-ba78-e944f9465763; wzws_cid=e639dacd26d2e70f17b8a3ceaa1a2086a7d3fe397f1e1a71396af200474c8551e49f41d297ac3105004644dc9e6cf2746bb165f120e27e5a2fd29e7a23f6c734b42a9d7f5b8950badd8a03bdebd62ab0; HM4hUBT0dDOn443T=41HOpG7_MJAvV4YMG_KBZJ0w6ojdQSbLpkXix6XnYw9wg500xOcby296L4NRVOGXOoBfRruZYRXletiLhIzikd3lpWmTz55fIptjG6UkSPDQUGwnjkb0.70QKpCZcJIne1NokXVBKRe91iMizQTl2KmtlhVK5r73.ORARaXzRnQpGQy42kzc6g4ZryxFDZvzyI2Sa1Fyd2bZOPMTD.j5V7pzdL3XhbPxvprDby4MBq6wjZij5vtOwpAMjkUbj62BH8Ny4mVJg6DWb9c3nyDGgRpqlMSepe.kotqWd4lhbJOdE0wQwXrgv_Y.S7AY3jWLNh47',
          # 注意，useragent不能改变，否则cookie失效
          'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        }
    def get_url_list(self,url_path,section):
        '''
        获取配置文件
        :param url_path:
        :return: list 配置文件内容
        '''
        conf = ConfigParser()  # 需要实例化一个ConfigParser对象
        conf.read(url_path)  # 需要添加上config.ini的路径，不需要open打开，直接给文件路径就读取，也可以指定encoding='utf-8'
        # str=conf.sections() #list ['urls']
        # s=conf.get('urls','浙江省高级人民法院') #获取'浙江省高级人民法院'的value值
        return conf.items(section)


if __name__ == '__main__':
    spider=CasesSpider()
    #读取配置文件里的urls内容
    section='urls'
    list =  spider.get_url_list('case_page_urls.ini',section)
    url=list[0][1]
    # for l in list:
    #     # l:('浙江省高级人民法院', 'https://wenshu.court.gov.cn/website/wenshu/181217BMTKHNT2W0/index.html?pageId=b74c0348f48323e0989104d60ecc29cb&s38=100&fymc=浙江省高级人民法院')
    #     fymc=l[0]
    #     url=l[1]
    #     print(l)
    html = requests.get(url=url, headers=spider.headers).text
    print(html)


