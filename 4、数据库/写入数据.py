from sqlalchemy import create_engine
# from pymysql import connect
import pandas as pd

conn=create_engine('mysql+pymysql://root:zhaoaiqq@localhost:3306/db_courts?charset=utf8')
# 使用 cursor() 方法创建一个游标对象 cursor
# cursor = conn.cursor()
# sql='''
# select * from weather_test where
# create_time between '2020-09-21' and '2020-09-22'
# and city in ('杭州','上海')
# '''

# sql='''
# INSERT INTO tb_judger ( id, juger_name, province, gender, court_name )
#                        VALUES
#                        ( 123, 'abc', 'js',1,'hih' );
# '''

data={'id':123343,
        'juger_name':'zhaoai',
        'province':'江苏省',
        'gender':1,
        'court_name':'测试法院名称'
      }
insert_df=pd.DataFrame([data])
# if_exists默认为fail则当存在表时，升起错误

insert_df.to_sql('tb_judger',conn,index=False,if_exists='append')
# df.to_sql('tb_judger',con=conn,index=False,if_exists='append')

print('ok')