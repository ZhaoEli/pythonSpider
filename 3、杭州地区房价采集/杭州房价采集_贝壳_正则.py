import re
import csv
from fake_useragent import UserAgent
import  time
import random
from urllib import request
import requests
'''
    二级静态页面抓取
    
    S1：获取页面page链接，并拼合URL
    S2：进入链接页面解析页面
    S3：装填页面
    
'''
class housing_Prices_Spider(object):
    def __init__(self):
        #一级页面的url
        self.one_url='https://hz.fang.ke.com/loupan/pg{page_number}'
        
        #设定一个浏览器代理小马甲
        self.headers = {'User-Agent': UserAgent().chrome}

        #保存文件的名字，不需要加后缀
        self.filename = '杭州房子价格2023.05.27'

        #二级页面需要拼合一下前缀，才能正常链接
        self.prefix_url='https://hz.fang.ke.com/'
        #一级页面
        self.re_bds_one = '<div class="resblock-desc-wrapper">.*?<a href="/(.*?)".*?<i class="icon location-icon"></i>(.*?)/(.*?)/'
        #二级页面
        self.re_bds_two = '<!-- 右边卡片 -->.*?class="animation">(.*?)</h2>.*?"tag-item sell-type-tag">(.*?)<.*?house-type-tag">(.*?)</span>.*?<span class="price-number">(.*?)</span>.*?class="price-unit">(.*?)<.*?"price-number.*?>(.*?)</.*?"price-unit">(.*?)<.*?class="content">(.*?)</span>.*?' \
                          '<span class="content">(.*?)</'
        
        #需要爬取网页的范围
        self.min_page_number=1
        self.max_page_number=2

    def get_html(self, m_url, headers):
        req=request.Request(url=m_url, headers=headers)
        res = request.urlopen(req)
        # res.encoding = 'utf-8'
        html = res.read().decode('utf-8', 'ignore')
        return html
    def parse_html(self, re_bds, html):
        pattern = re.compile(re_bds,re.S)
        re_list = pattern.findall(html)
        return re_list
    def second_list_to_write(self, prefix_url, re_bds_two, re_list_one):
        for r in re_list_one:
            url = prefix_url+r[0]
            two_html=self.get_html(m_url=url,headers=self.headers)
            two_list=self.parse_html(re_bds=re_bds_two, html=two_html)
            flag_list = []
            if len(two_list):
                for s in two_list[0]:
                    flag_list.append(s)
            else:
                pass
            for s in r[1:]:
                flag_list.append(s)
            flag_list.append(url)
            self.save_to_CSV(filename=self.filename,list=flag_list)
            print(flag_list)
            time.sleep(random.randint(1, 2))

    def save_to_CSV(self, filename, list):

        filename=filename+'.csv'
        with open(filename, 'a', newline='', encoding='utf-8') as f:
            w = csv.writer(f,delimiter=',')
            w.writerow(list)

    def run(self):

        for page_number in range(self.min_page_number,self.max_page_number+1):
            one_url=self.one_url.format(page_number=page_number)
            html = self.get_html(m_url=one_url, headers=self.headers)
            #获取一级页面内容的链接，准备做跳转到二级
            one_list = self.parse_html(self.re_bds_one, html)
            #获取二级详情页并写入csv
            # self.second_list_to_write(self.prefix_url,self.re_bds_two,one_list)
            for u in one_list:
                second_url=self.prefix_url+u[0]
                html = requests.get(url=second_url, headers=self.headers).text
                list = self.parse_html(self.re_bds_two, html)
                pass



            print('获取完成第{d}个页面——————————over————————————————'.format(d=page_number))
        print('ok,程序运行完毕，抓取了{page_one}~{page_two}页的数据。'.format(page_one=self.min_page_number,page_two=self.max_page_number))


#主函数
if __name__ == '__main__':
    try:
        spider = housing_Prices_Spider()
        spider.run()
    except Exception as e:
        print(e)
