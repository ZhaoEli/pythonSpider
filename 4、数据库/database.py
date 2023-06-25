import pymysql

#创建链接
con=pymysql.connect(host='localhost',user='root',password='zhaoaiqq',database='mysql',port=3306)

#创建游标对象
cur=con.cursor()

print(con.host_info)
sql1='''
CREATE TABLE `db_juger`
(   
    id varchar(50),
    name        varchar(50) comment '法官姓名',
    province    VARCHAR(50) comment '省份区域',
    gender      int     comment '1 男
0 女',
    court_name  varchar(50) comment '法庭名称',
    court_office  varchar(50) comment '法官所在法庭号',
    department  varchar(50) comment '所在部门',
    title       varchar(50) comment '头衔',
    office_position  varchar(50) comment '职位',
    last_update DATE    comment '最后更新时间'
)
    comment '法官数据库';
'''

sql2='''
CREATE TABLE `alter` (first_day DATE, last_day DATE);
'''

try:
    #执行sql
    cur.execute(sql1)
    print('ok')

except Exception as  e:
    print(e)
    print('创建失败了！')
finally:
    #关闭游标
    cur.close()
    #关闭数据库链接
    con.close()
