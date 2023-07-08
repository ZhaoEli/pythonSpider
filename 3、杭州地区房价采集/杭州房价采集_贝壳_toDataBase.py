import csv
import uuid
from fake_useragent import UserAgent
from lxml import etree
import requests
import random
import  time
import datetime
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
        # self.one_url = 'https://hz.fang.ke.com/loupan/pg{page_number}'
        self.one_url ='https://hz.fang.ke.com/loupan/fuyang/pg{page_number}'
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
        清洗数据
        :param parse_html:
        :param xpath_bds:
        :return:
        '''
        li = parse_html.xpath(xpath_bds)  # 抓取数据
        # 如果抓取不到数据，li为空表，则赋值为空字符串，如果抓取到则提取
        li = li[0].strip() if li else ''
        return li.replace(' ','')

    def sql_query(self, column_list, value_list):
        '''
        向数据库里取数
        :param column_list: 取的字段
        :param value_list: 取值
        :return: id 和当前的字段
        :type: dataframe
        '''
        sql = '''
        select house_id, {column}
        from DB_HOUSE_PRICES.house_item 
        where house_name = "{house_name}" and house_type="{house_type}"
        '''.format(column=','.join(column_list), house_name=value_list[0], house_type=value_list[1])
        dataframe = pd.read_sql_query(sql=sql, con=self.conn)
        return dataframe

    def get_xpathRds(self):
        '''
        生成网页所需的xpath
        :return: ditc
        '''
        dict={}
        dict.update({'zone':".//a[@class='resblock-location']/text()"}) # 楼盘所处板块
        dict.update({'name':".//div/h2[@class='DATA-PROJECT-NAME']/text()"})
        dict.update({'other_name':  ".//div[@class='other-name']/text()"})
        dict.update({'price':".//div[@class='top-info ']/div[@class='price']/span[@class='price-number']/text() | .//div[@class='info-wrap']/div[@class='top-info ']/div[@class='price']/span[@class='price-unit']/text()"})# unit=""
        # value=".//div[@class='top-info ']/div[@class='price']/span[@class='price-number'][2]/text()"
        # value_unit = ".//div[@class='top-info ']/div[@class='price']/span[@class='price-unit'][1]/text()"
        dict.update({'tag_item':".//div[@class='title-wrap']/div[1]/div[@class='tags-wrap']/span[@class='tag-item sell-type-tag']/text()"})
        dict.update({'house_type':".//div[@class='title-wrap']/div[1]/div[@class='tags-wrap']/span[@class='tag-item house-type-tag']/text()"})
        dict.update({'address':".//div[@class='resblock-info animation qr-fixed post_ulog_exposure_scroll']/div[@class='info-wrap']/div[@class='middle-info animation']/ul[@class='info-list']/li[@class='info-item'][1]/span[@class='content']/text()"})
        dict.update({'new_open_date':".//div[@class='resblock-info animation qr-fixed post_ulog_exposure_scroll']/div[@class='info-wrap']/div[@class='middle-info animation']/ul[@class='info-list']/li[@class='info-item open-date-wrap']/div[@class='open-date']/span[@class='content']/text()"})
        dict.update({'rooms' : ".//div[@class='resblock-info animation qr-fixed post_ulog_exposure_scroll']/div[@class='info-wrap']/div[@class='middle-info animation']/ul[@class='info-list']/li[@class='info-item'][2]/span[@class='content']/span[@class='house-type-item']/text()"})
        dict.update({'collecting_time' : str(datetime.date.today()) }) # 数据采集时间
        dict.update({'feature' :".//span[@class='label-val tese-val']/text()"})
        dict.update({'builders' :".//ul[@class='x-box'][1]/li[@class='all-row'][3]/span[@class='label-val']/text()"})
        return dict
    def get_xpathRds_info_page(self):
        dict={}
        # dict.update({'property_type':".//ul[@class='x-box'][1]/li[1]/span[@class='label-val']/text()"})#'物业类型',
        dict.update({'refer_price':".//ul[@class='x-box'][1]/li[2]/span[@class='label-val']/span/text()"})#'参考价格',
        # house_area = ''          # '平方数,单位㎡',
        # open_date            #'最近开盘',
        dict.update({'place':".//span[@class='label-val']/a/text()"})# '区域',
        dict.update({'address':".//ul[@class='x-box'][1]/li[@class='all-row'][1]/span[@class='label-val']/text()"})              # '地址',
        dict.update({'building_type':".//ul[@class='x-box'][2]/li[1]/span[@class='label-val']/text()"})       #'房产类型',
        dict.update({'zhandi_area' :".//ul[@class='x-box'][2]/li[3]/span[@class='label-val']/text()"})       #'占地面积',
        dict.update({'quyu_area':".//ul[@class='x-box'][2]/li[5]/span[@class='label-val']/text()"})       #'区域面积',
        dict.update({'blocks'   :".//ul[@class='x-box'][2]/li[7]/span[@class='label-val']/text()"})            #'规划户数',
        dict.update({'years_limit'  :".//ul[@class='x-box'][2]/li[@class='all-row'][1]/span[@class='label-val'][1]/text()"})        #'产权年限',
        dict.update({'recently_handed_over':".//ul[@class='x-box'][2]/li[@class='all-row'][3]/span[@class='label-val']/text()"}) #'最近交房',
        dict.update({'greening_rate'    :".//ul[@class='x-box'][2]/li[2]/span[@class='label-val']/text()"})    #' 绿化率',
        dict.update({'volume_rate'     :   ".//ul[@class='x-box'][2]/li[4]/span[@class='label-val']/text()"})  #'容积率',
        dict.update({'property_type' :".//ul[@class='x-box'][2]/li[6]/span[@class='label-val']/text()"})      #'物业费',
        dict.update({'water_supply_method':".//ul[@class='x-box'][3]/li[5]/span[@class='label-val']/text()"})  #'供水方式',
        dict.update({'property_costs':".//ul[@class='x-box'][3]/li[3]/span[@class='label-val']/text()"}) # 物业费
        dict.update({'parking_numbers' :".//ul[@class='x-box'][3]/li[7]/span[@class='label-val']/text()"})     #'车位',
        dict.update({'parking_ratio'  :".//ul[@class='x-box'][3]/li[2]/span[@class='label-val']/text()"})      #'车位配比',
        dict.update({'heating_method'  :".//ul[@class='x-box'][3]/li[4]/span[@class='label-val']/text()"})     #' 供暖方式',
        dict.update({'power_supply'  :".//ul[@class='x-box'][3]/li[6]/span[@class='label-val']/text()"})  #'供电方式',
        dict.update({'open_date':".//ul[@class='x-box'][2]/li[@class='all-row'][3]/span[@class='label-val']/text()"}) #开盘时间
        return  dict
    def get_house_info(self):
        # 读取数据库
        sql = 'select * from DB_HOUSE_PRICES.house_item'
        house_info = pd.read_sql_query(sql=sql, con=self.conn)
        return house_info

    def get_buildings_BaseInfo(self, min_page_number, max_page_number):
        '''
        1、如有新增楼盘，增量写入
        2、如果有楼盘名称存在，则不处理
        :param min_page_number:
        :param max_page_number:
        :return:
        '''
        xpath_bds=self.get_xpathRds() #获取xpath
        for page_number in range(min_page_number, max_page_number + 1):
            one_url = self.one_url.format(page_number=page_number)
            one_url_list = self.get_List(one_url, self.headers, self.re_bds_url)
            one_zone_list = self.get_List(one_url, self.headers, xpath_bds.get('zone'))

            for i in range(0, len(one_url_list)):
                # 获取楼盘页面信息
                two_url = self.prefix_url + one_url_list[i]
                html1 = requests.get(url=two_url, headers=self.headers).text
                parse_html = etree.HTML(html1)
                t_name = self.get_realValue(parse_html,xpath_bds.get( 'name'))  # 楼盘名
                t_house_type = self.get_realValue(parse_html, xpath_bds.get('house_type'))  # 房屋类型 住宅 商用 商住两用

                # 查询楼盘之前是否记录过
                flag = self.sql_query(column_list=['house_name', 'house_type'], value_list=[t_name, t_house_type])
                if flag.empty:
                    t_other_name = self.get_realValue(parse_html, xpath_bds.get('other_name'))  # 别名
                    t_other_name = t_other_name.replace('别名：', '')
                    # t_price= parse_html.xpath(price) #单价
                    t_sale_status = self.get_realValue(parse_html, xpath_bds.get('tag_item'))  # 是否在售
                    t_address = self.get_realValue(parse_html,xpath_bds.get('address') )  # 地址
                    t_new_open_date = self.get_realValue(parse_html, xpath_bds.get('new_open_date'))  # 最新开盘
                    if t_new_open_date == '':
                        t_new_open_date = self.get_realValue(parse_html,
                                                             ".//div[@class='resblock-info animation qr-fixed post_ulog_exposure_scroll']/div[@class='info-wrap']/div[@class='middle-info animation']/ul[@class='info-list']/li[@class='info-item'][2]/span[@class='content']/text()")
                    t_rooms = parse_html.xpath(xpath_bds.get('rooms'))  # 几室
                    house_zone = one_zone_list[i].strip()
                    # 获取"更多"详情页
                    html = requests.get(url=two_url + "xiangqing/", headers=self.headers).text
                    parse_html = etree.HTML(html)
                    t_feature = self.get_realValue(parse_html, xpath_bds.get('feature'))  # 特色描述：成熟商圈 品牌房企 VR看房 绿化率高
                    t_builders = self.get_realValue(parse_html, xpath_bds.get('builders'))  # 开发商

                    # 拼字段成一个字典，方便写入
                    dict = {}
                    dict.update({'house_name': t_name})
                    dict.update({'collecting_time': collecting_time})
                    dict.update({'other_name': t_other_name})
                    dict.update({'house_zone': house_zone})
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
                    print('{} —Sucess！**页面={}'.format(t_name, page_number))
                else:
                    print('{} ————已经存在，直接跳过，状态：pass！**页面={}'.format(t_name,page_number))
                time.sleep(random.randint(1, 2))

            print('*********第{d}个页面*****over******获取完成！\n'.format(d=page_number))
    def write_house_price(self):
        #读取数据库
        house_info=self.get_house_info()
        #获取xpath
        xpath_dict=g=self.get_xpathRds()
        for index, row in house_info[419:].iterrows():
            id=row['house_id']
            name=row['house_name']
            url=row['url_source']
            html_content = requests.get(url=url, headers=self.headers).text
            parse_html = etree.HTML(html_content)

            # 开始提取数据，先提取url的数据，放入house_price表中
            dict = {}
            dict.update({'mark_labe': 0})  # 0 在售楼盘价格 1 二手房价格
            dict.update({'house_id': id})
            dict.update({'house_name': name})
            dict.update({'update_time': datetime.date.today()})
            # 判断当前数据是否已经采集，如果有则pass，否则写入数据
            sql = '''
                    select * 
                    from DB_HOUSE_PRICES.house_price
                    where house_id = "{id}" 
                    and mark_labe="{mark_labe}"
                    and update_time="{update_time}"
                    '''\
                .format(id=id,
                        mark_labe=dict.get('mark_labe'),
                        update_time=dict.get('update_time')
                        )
            df_temp = pd.read_sql_query(sql=sql, con=self.conn)
            flag=df_temp.empty
            if  df_temp.empty:
                price_list=self.get_List(m_url=url,headers=self.headers,re_bds=xpath_dict.get('price'))
                if not price_list:
                    pass
                elif len(price_list)==4:
                    dict.update({'price': price_list[0]})
                    dict.update({'unit': price_list[1]})
                    dict.update({'value': price_list[2]})
                    dict.update({'value_unit': price_list[1]})
                elif len(price_list)==2:
                    dict.update({'price': price_list[0]})
                    dict.update({'unit': price_list[1]})
                dataframe=pd.DataFrame.from_dict(dict,orient='index').T
                # print(dataframe)
                dataframe.to_sql('house_price', self.conn, if_exists='append', index=False)
                print(name,'写入sucess!index=',index)
            else: print(name,' :当前已经采集！pass！index=',index)
            time.sleep(random.randint(1, 3))
    def write_house_info(self):
        '''
        写入楼盘详情。
        数据表：houser_info
        :return:
        '''
        house_info=self.get_house_info()
        # 遍历 DataFrame 中的每一行数据
        for index, row in house_info[1167:].iterrows():
            id=row['house_id']
            name=row['house_name']
            url=row['url_source']+'xiangqing'
            html_content = requests.get(url=url, headers=self.headers).text
            parse_html = etree.HTML(html_content)
            # 开始提取数据，先提取url的数据，放入house_price表中
            dict = {}
            dict.update({'house_id': id})
            dict.update({'house_name': name})
            dict.update({'update_time': datetime.date.today()})
            # 判断当前数据是否已经采集，如果有则pass，否则写入数据
            sql = '''select house_id,house_name from DB_HOUSE_PRICES.house_info where house_id = "{id}" '''\
                .format(id=id)
            #生成详情页面的xpath
            xpath = self.get_xpathRds_info_page()
            #从数据库获取楼盘的基本信息，如有已经存在那就返回数据，否则为空
            df_temp = pd.read_sql_query(sql=sql, con=self.conn)
            #判断数据是否存在
            if  df_temp.empty:
                for key , value in xpath.items():
                    # print(key, value)
                    str=self.get_realValue(parse_html=parse_html,xpath_bds=value)
                    dict.update({key: str})
                dataframe=pd.DataFrame.from_dict(dict,orient='index').T
                # print(dataframe)
                dataframe.to_sql('house_info', self.conn, if_exists='append', index=False)
                print(name,'写入sucess!,index=',index)
            else: print(name,' :info 当前已经采集！pass！index=',index)
            time.sleep(random.randint(1, 2))


    def run(self,min_page_number, max_page_number):

        self.write_house_price()
        # self.write_house_info()

# 主函数
if __name__ == '__main__':

    # 需要爬取网页的范围
    min_page_number = 1  # 从当前页开始采集
    max_page_number = 8 # 终止页面，采集数据包括当前页。📢

    try:
        spider = housing_Prices_Spider()
        spider.run(min_page_number, max_page_number)
    except Exception as e:
        print(e)
