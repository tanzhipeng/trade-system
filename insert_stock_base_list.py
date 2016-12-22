import pymysql
import tushare as ts

#write a function to get the base information of the stock
#



stock_list = ts.get_stock_basics()
stock_600732 = stock_list.ix['600732']

#print(stock_600732.industry.encode('GBK'))

conn = pymysql.connect(host='192.168.0.102',unix_socket='3306',user='stock_user',passwd='Ws143029',db='stock_datebase')
cur = conn.cursor()
cur.execute("use stock_database")

cur.execute("insert into stock_base_list(s_code,s_name,s_industry,s_area,s_timetomarket,s_total) values (%s,%s,%s,%s,%s,%s)",
('600737',stock_600732.name.decode('latin-1').encode('utf-8'),stock_600732.industry.decode('GBK').encode('utf-8'),stock_600732.area.decode('latin-1'), 1111, 44638.3))

cur.connection.commit()
cur.close()
conn.close()

#cur.execute("insert into stock_base_list(s_code,s_name,s_industry,s_area,s_timetomarket,s_total) values (\"%s\",\"%s\",\"%s\",\"%s\",\"%d\",\"%f\")",
#('600732',stock_600732.name,stock_600732.industry,stock_600732.area, stock_600732.timeToMarket.astype(int), stock_600732.totals.astype(float)))
