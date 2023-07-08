import csv
import uuid

from fake_useragent import UserAgent
import time
import requests
import random
import datetime
from lxml import etree
from sqlalchemy import create_engine
import pandas as pd

# from lxml.html import fromstring,tostring
'''
    二级静态页面抓取
    
    S1：获取页面page链接，并拼合URL
    S2：进入链接页面解析页面
    S3：装填页面
    
'''


class housing_Prices_Spider(object):
    def __init__(self):
        # 创建连接器
        self.conn = create_engine('mysql+pymysql://root:zhaoaiqq@localhost:3306/DB_HOUSE_PRICES?charset=utf8')

        # 一级页面的url
        self.one_url = 'https://hz.fang.ke.com/loupan/pg{page_number}'

        # 设定一个浏览器代理小马甲
        self.headers = {'User-Agent': UserAgent().chrome}

        # 二级页面需要拼合一下前缀，才能正常链接
        self.prefix_url = 'https://hz.fang.ke.com'
        # 楼盘地址
        self.re_bds_url = ".//div[@class='resblock-name']/a[@class='name ']/@href"

    def get_List(self, m_url, headers, re_bds):
        html1 = requests.get(url=m_url, headers=headers).text
        html1 = html1.replace('\n\t\t\t', '')
        parse_html = etree.HTML(html1)
        # 基准 xpath 表达式，url的节点对象
        # url_list = parse_html.xpath(self.re_bds_name)
        # list=url_list[0].attrib
        # print(list['href'])
        url_list = parse_html.xpath(re_bds)
        return url_list

    def get_realValue(self, parse_html, xpath_bds):
        '''
        :param parse_html:
        :param xpath_bds:
        :return:
        '''
        li = parse_html.xpath(xpath_bds)  # 抓取数据
        # 如果抓取不到数据，li为空表，则赋值为空字符串，如果抓取到则提取
        li = li[0].strip() if li else ''
        return li

    def sql_query(self, column_list, value_list):
        '''
        向数据库里取数
        :param column_list: 取的字段
        :param value_list: 取值
        :return: id 和当前的字段
        :type: dataframe
        '''
        sql = '''
        select house_id, {column} ,house_type
        from DB_HOUSE_PRICES.house_item 
        where house_name="{house_name}" and house_type="{house_type}"
        '''.format(column=','.join(column_list), house_name=value_list[0], house_type=value_list[1])
        dataframe = pd.read_sql_query(sql=sql, con=self.conn)
        return dataframe

    def write_data(self):
        pass

    def run(self, min_page_number, max_page_number):
        # 打开文件写入端口
        # filename=self.filename+'.csv'
        # f =open(filename, 'a', newline='', encoding='utf-8')
        # w = csv.writer(f,delimiter=',')
        # 设置rebds匹配规则
        zone = ".//a[@class='resblock-location']/text()"  # 楼盘所处板块
        name = ".//div/h2[@class='DATA-PROJECT-NAME']/text()"
        other_name = ".//div[@class='other-name']/text()"
        price = ".//div[@class='top-info ']/div[@class='price']/span[@class='price-number']/text() | .//div[@class='info-wrap']/div[@class='top-info ']/div[@class='price']/span[@class='price-unit']/text()"
        # unit=""
        # value=".//div[@class='top-info ']/div[@class='price']/span[@class='price-number'][2]/text()"
        # value_unit = ".//div[@class='top-info ']/div[@class='price']/span[@class='price-unit'][1]/text()"
        tag_item = ".//div[@class='title-wrap']/div[1]/div[@class='tags-wrap']/span[@class='tag-item sell-type-tag']/text()"
        house_type = ".//div[@class='title-wrap']/div[1]/div[@class='tags-wrap']/span[@class='tag-item house-type-tag']/text()"
        address = ".//div[@class='resblock-info animation qr-fixed post_ulog_exposure_scroll']/div[@class='info-wrap']/div[@class='middle-info animation']/ul[@class='info-list']/li[@class='info-item'][1]/span[@class='content']/text()"
        new_open_date = ".//div[@class='resblock-info animation qr-fixed post_ulog_exposure_scroll']/div[@class='info-wrap']/div[@class='middle-info animation']/ul[@class='info-list']/li[@class='info-item open-date-wrap']/div[@class='open-date']/span[@class='content']/text()"
        rooms = ".//div[@class='resblock-info animation qr-fixed post_ulog_exposure_scroll']/div[@class='info-wrap']/div[@class='middle-info animation']/ul[@class='info-list']/li[@class='info-item'][2]/span[@class='content']/span[@class='house-type-item']/text()"
        collecting_time = str(datetime.date.today())  # 数据采集时间
        feature = ".//span[@class='label-val tese-val']/text()"
        builders = ".//ul[@class='x-box'][1]/li[@class='all-row'][3]/span[@class='label-val']/text()"

        for page_number in range(min_page_number, max_page_number + 1):
            one_url = self.one_url.format(page_number=page_number)
            one_url_list = self.get_List(one_url, self.headers, self.re_bds_url)
            one_zone_list = self.get_List(one_url, self.headers, zone)

            for i in range(0, len(one_url_list)):
                # 获取楼盘页面信息
                two_url = self.prefix_url + one_url_list[i]
                html1 = requests.get(url=two_url, headers=self.headers).text
                parse_html = etree.HTML(html1)
                t_name = self.get_realValue(parse_html, name)  # 楼盘名
                t_house_type = self.get_realValue(parse_html, house_type)  # 房屋类型 住宅 商用 商住两用

                # 查询楼盘之前是否记录过
                flag = self.sql_query(column_list=['house_name', 'house_type'], value_list=[t_name, t_house_type])
                if flag.empty:
                    t_other_name = self.get_realValue(parse_html, other_name)  # 别名
                    t_other_name = t_other_name.replace('别名：', '')
                    # t_price= parse_html.xpath(price) #单价
                    t_sale_status = self.get_realValue(parse_html, tag_item)  # 是否在售
                    t_address = self.get_realValue(parse_html, address)  # 地址
                    t_new_open_date = self.get_realValue(parse_html, new_open_date)  # 最新开盘
                    if t_new_open_date == '':
                        t_new_open_date = self.get_realValue(parse_html,
                                                             ".//div[@class='resblock-info animation qr-fixed post_ulog_exposure_scroll']/div[@class='info-wrap']/div[@class='middle-info animation']/ul[@class='info-list']/li[@class='info-item'][2]/span[@class='content']/text()")
                    t_rooms = parse_html.xpath(rooms)  # 几室
                    house_zone = one_zone_list[i].strip()
                    # 获取"更多"详情页
                    html = requests.get(url=two_url + "xiangqing/", headers=self.headers).text
                    parse_html = etree.HTML(html)
                    t_feature = self.get_realValue(parse_html, feature)  # 特色描述：成熟商圈 品牌房企 VR看房 绿化率高
                    t_builders = self.get_realValue(parse_html, builders)  # 开发商

                    # 拼字段成一个list，方便按行写入
                    dict = {}
                    dict.update({'house_name': t_name})
                    dict.update({'collecting_time': collecting_time})
                    dict.update({'other_name': t_other_name})
                    dict.update({'house_zone': house_zone})
                    # if len(t_price) ==4: #price是单独的数组
                    # 如果又有单价又有总价，需要重新处理，拆分开
                    #     dict.update({'price':t_price[0]})
                    #     dict.update({'uint': t_price[1]})
                    #     dict.update({'value': t_price[2]})
                    #     dict.update({'value_uint': t_price[3]})
                    # elif len(t_price) ==2:
                    #     dict.update({'price':t_price[0]})
                    #     dict.update({'uint': t_price[1]})
                    # else: dict.update({'price':''})

                    dict.update({'sale_status': t_sale_status})
                    dict.update({'house_type': t_house_type})
                    dict.update({'address': t_address})
                    # dict.update({'new_open_date':t_new_open_date})
                    # 转换rooms为字符串
                    dict.update({'rooms': ','.join(t_rooms) if t_rooms else ''})
                    dict.update({'features': t_feature})
                    dict.update({'builders': t_builders})
                    dict.update({'url_source': two_url})  # url地址
                    dict.update({'house_id': str(uuid.uuid1()).replace('-', '')})
                    # dataframe = pd.DataFrame(dict, index=[0])
                    dataframe=pd.DataFrame.from_dict(dict,orient='index').T
                    dataframe.to_sql('house_item', self.conn, if_exists='append', index=False)
                    print('{} ————写入完成，ok！**页面={}'.format(t_name, page_number))
                else:
                    print('{} ————已经存在，**页面={}，直接跳过，状态：failed！'.format(t_name,page_number))
                time.sleep(random.randint(1, 2))

            print('*********第{d}个页面*****over******获取完成！'.format(d=page_number))



# 主函数
if __name__ == '__main__':

    # 需要爬取网页的范围
    min_page_number = 28  # 从当前页开始采集
    max_page_number = 40  # 终止页面，采集数据包括当前页。📢

    try:
        spider = housing_Prices_Spider()
        spider.run(min_page_number, max_page_number)
    except Exception as e:
        print(e)
