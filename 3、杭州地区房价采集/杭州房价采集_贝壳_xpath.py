import re
import csv
from fake_useragent import UserAgent
import  time
import requests
import random
import datetime
from lxml import etree
from lxml.html import fromstring,tostring
'''
    二级静态页面抓取
    
    S1：获取页面page链接，并拼合URL
    S2：进入链接页面解析页面
    S3：装填页面
    
'''
class housing_Prices_Spider(object):
    def __init__(self):
        #设置写入的文件名：贝壳房价采集_2022.08.03
        self.filename = './hangzhou_price/贝壳房价采集_'+str(datetime.date.today())

        #一级页面的url
        self.one_url='https://hz.fang.ke.com/loupan/pg{page_number}'
        
        #设定一个浏览器代理小马甲
        self.headers = {'User-Agent': UserAgent().chrome}

        #二级页面需要拼合一下前缀，才能正常链接
        self.prefix_url='https://hz.fang.ke.com'
        #楼盘地址
        self.re_bds_url = ".//div[@class='resblock-name']/a[@class='name ']/@href"

    def get_List(self, m_url, headers,re_bds):
        html1=requests.get(url=m_url,headers=headers).text
        html1=html1.replace('\n\t\t\t','')
        parse_html = etree.HTML(html1)
        # 基准 xpath 表达式，url的节点对象
        # url_list = parse_html.xpath(self.re_bds_name)
        # list=url_list[0].attrib
        # print(list['href'])
        url_list = parse_html.xpath(re_bds)
        return url_list
    def get_realValue(self,parse_html,xpath_bds):
        li = parse_html.xpath(xpath_bds)  # 抓取数据
        #如果抓取不到数据，li为空表，则赋值为空字符串，如果抓取到则提取
        li = li[0].strip() if li else ''
        return li


    def run(self,min_page_number,max_page_number):
        #打开文件写入端口
        filename=self.filename+'.csv'
        f =open(filename, 'a', newline='', encoding='utf-8')
        w = csv.writer(f,delimiter=',')
        #设置rebds匹配规则
        area=".//a[@class='resblock-location']/text()" #楼盘所处板块
        name=".//div/h2[@class='DATA-PROJECT-NAME']/text()"
        other_name=".//div[@class='other-name']/text()"
        price=".//div[@class='top-info ']/div[@class='price']/span[@class='price-number']/text() | .//div[@class='info-wrap']/div[@class='top-info ']/div[@class='price']/span[@class='price-unit']/text()"
        # unit=""
        # value=".//div[@class='top-info ']/div[@class='price']/span[@class='price-number'][2]/text()"
        # value_unit = ".//div[@class='top-info ']/div[@class='price']/span[@class='price-unit'][1]/text()"
        tag_item=".//div[@class='title-wrap']/div[1]/div[@class='tags-wrap']/span[@class='tag-item sell-type-tag']/text()"
        house_type=".//div[@class='title-wrap']/div[1]/div[@class='tags-wrap']/span[@class='tag-item house-type-tag']/text()"
        address=".//div[@class='resblock-info animation qr-fixed post_ulog_exposure_scroll']/div[@class='info-wrap']/div[@class='middle-info animation']/ul[@class='info-list']/li[@class='info-item'][1]/span[@class='content']/text()"
        new_open_date=".//div[@class='resblock-info animation qr-fixed post_ulog_exposure_scroll']/div[@class='info-wrap']/div[@class='middle-info animation']/ul[@class='info-list']/li[@class='info-item open-date-wrap']/div[@class='open-date']/span[@class='content']/text()"
        rooms=".//div[@class='resblock-info animation qr-fixed post_ulog_exposure_scroll']/div[@class='info-wrap']/div[@class='middle-info animation']/ul[@class='info-list']/li[@class='info-item'][2]/span[@class='content']/span[@class='house-type-item']/text()"
        collecting_time=str(datetime.date.today()) #数据采集时间
        feature =".//span[@class='label-val tese-val']/text()"
        builders = ".//ul[@class='x-box'][1]/li[@class='all-row'][3]/span[@class='label-val']/text()"

        for page_number in range(min_page_number,max_page_number ):

            one_url=self.one_url.format(page_number=page_number)
            one_url_list=self.get_List(one_url,self.headers,self.re_bds_url)
            one_area_list=self.get_List(one_url,self.headers,area)

            for i in range(0,len(one_url_list)):
                # 获取楼盘页面信息
                two_url=self.prefix_url+one_url_list[i]
                html1 = requests.get(url=two_url, headers=self.headers).text
                parse_html = etree.HTML(html1)

                t_name = self.get_realValue(parse_html,name) #楼盘名
                print(t_name)
                t_other_name = self.get_realValue(parse_html, other_name) #别名
                t_other_name= t_other_name.replace('别名：','')

                t_price= parse_html.xpath(price) #单价
                # t_unit = parse_html.xpath(unit) #单价单位
                # t_value = parse_html.xpath(price)[1].strip() # 总价
                # t_value_unit = parse_html.xpath(unit)[1].strip() #总价单位
                t_sale_status = self.get_realValue(parse_html, tag_item) #是否在售
                t_house_type = self.get_realValue(parse_html, house_type) #房屋类型 住宅 商用 商住两用
                t_address = self.get_realValue(parse_html, address) #地址
                t_new_open_date = self.get_realValue(parse_html, new_open_date) #最新开盘
                if t_new_open_date=='' :
                    t_new_open_date = self.get_realValue(parse_html,".//div[@class='resblock-info animation qr-fixed post_ulog_exposure_scroll']/div[@class='info-wrap']/div[@class='middle-info animation']/ul[@class='info-list']/li[@class='info-item'][2]/span[@class='content']/text()")
                t_rooms = parse_html.xpath(rooms) #几室
                t_areas=one_area_list[i].strip()
                # 获取"更多"详情页
                html = requests.get(url=two_url + "xiangqing/", headers=self.headers).text
                parse_html = etree.HTML(html)
                t_feature= self.get_realValue(parse_html, feature) #特色描述：成熟商圈 品牌房企 VR看房 绿化率高
                t_builders = self.get_realValue(parse_html, builders) #开发商

                # 拼字段成一个list，方便按行写入
                dict = {}
                dict.update({'name':t_name})
                dict.update({'collecting_time': collecting_time})
                dict.update({'other_name':t_other_name})
                dict.update({'area':t_areas})
                if len(t_price) ==4: #price是单独的数组
                    dict.update({'price':t_price[0]})
                    dict.update({'uint': t_price[1]})
                    dict.update({'value': t_price[2]})
                    dict.update({'value_uint': t_price[3]})
                elif len(t_price) ==2:
                    dict.update({'price':t_price[0]})
                    dict.update({'uint': t_price[1]})
                else: dict.update({'price':''})

                dict.update({'sale_status':t_sale_status})
                dict.update({'house_type':t_house_type})
                dict.update({'address':t_address})
                dict.update({'new_open_date':t_new_open_date})
                dict.update({'rooms':t_rooms if t_rooms else ''})
                dict.update({'features':t_feature})
                dict.update({'builders': t_builders})
                dict.update({'url_source': two_url})#url地址
                w.writerow([dict])
                time.sleep(random.randint(1, 2))
            print('获取完成第{d}个页面——————————over————————————————'.format(d=page_number))
        f.close()


    # def run(self):
    #     for page_number in range(self.min_page_number,self.max_page_number+1):
    #         one_url=self.one_url.format(page_number=page_number)
    #         html = self.get_html(m_url=one_url, headers=self.headers)
    #         #获取一级页面内容的链接，准备做跳转到二级
    #         one_list = self.parse_html(self.re_bds_one, html)
    #         #获取二级详情页并写入csv
    #         self.second_list_to_write(self.prefix_url,self.re_bds_two,one_list)
    #         print('获取完成第{d}个页面——————————over————————————————'.format(d=page_number))
    #     print('ok,程序运行完毕，抓取了{page_one}~{page_two}页的数据。'.format(page_one=self.min_page_number,page_two=self.max_page_number))


#主函数
if __name__ == '__main__':

    # 需要爬取网页的范围
    min_page_number = 60 #从当前页开始采集
    max_page_number = 81 #终止页面，采集数据不包括当前页。注意！！📢

    try:
        spider = housing_Prices_Spider()
        spider.run(min_page_number,max_page_number)
    except Exception as e:
        print(e)
