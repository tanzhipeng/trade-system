import pymysql
import tushare as ts
import datetime
from pandas import DataFrame,Series
from common_tools import getNowDateToStr
from db_tools import generate_db_link,execute_many_to_db,select_from_db


#write a function to insert or refresh the daily price of given stock
#pseudo-code:
# 1.input: a.stock_code  code of stock  b.start_date date=None   c.end_date date=None  d.fq_type=None
# 2.if start_date is None, use tushare to initial the parameter, if end_date is None ,use the cursorrent date
# 2.get daily stock price and restore the data to a dataframe
# 3.create a database link
# 4.loop the database,and insert every element into the table 'stock_price_day'
# 5.close the database


#update the price data of stock with the code given until the last availble date of open market
#1.get the latest date(mark it to l_date) from the database by the stock_code
#2.if the l_date equals to the current date,do nothing else go to step3
#2.fetch the  dataframe by execute function ts.get_h_data() given the latest date to the start augument and the current date to the end augument
#3.if the length of result dataframe is 0,do nothing, else call insert_price_by_stockcode method between the startdate and enddate


def update_price_by_stocks_combination(stocks_code_series,fqtype='qfq',cursor=None):
    stock_base_list = ts.get_stock_basics()
    stocks_code_series.apply(update_price_by_stockcode, args=(stock_base_list,fqtype,cursor))


def update_price_by_stockcode(stock_code,stock_base_list,fqtype='qfq',cursor=None):

    cursor.execute('SELECT MAX(s_date) FROM stock_price_day WHERE s_code = %s',(stock_code,))

    latest_date = cursor.fetchone()[0]

    if latest_date is not None:

        latest_date_str = latest_date.strftime('%Y-%m-%d')
        now_date_str = getNowDateToStr()

        if latest_date_str != now_date_str:
            start_date_str = latest_date.replace(day=latest_date.day+1).strftime('%Y-%m-%d')
            #df = ts.get_h_data(stock_code,start=start_date_str,end=now_date_str)
            #if df is not None:
            #(stock_code,start_date=None,end_date=None,fq_type='qfq',stock_base_list=None,cursor=None)
            insert_stock_data_by_code(stock_code,start_date_str,now_date_str,fqtype,stock_base_list,cursor)
    else:
        insert_stock_data_by_code(stock_code=stock_code,fqtype=fqtype,stock_base_list=stock_base_list,cursor=cursor)


#insert the price data of the combination of stocks to the database
#The input argument is sequence which contain the code of stocks
def insert_price_by_stocks_combination(stocks_code_series,start_date=None,end_date=None,fqtype='qfq',cursor=None):

    stock_base_list = ts.get_stock_basics()
    stocks_code_series.apply(insert_stock_data_by_code,args=(start_date,end_date,fqtype,stock_base_list,cursor))


def insert_stock_data_by_code(stock_code,start_date=None,end_date=None,fq_type='qfq',stock_base_list=None,cursor=None):

    if stock_base_list is None:
        stock_base_list = ts.get_stock_basics()

    if start_date == None:
        start_date = datetime.datetime.strptime(str(stock_base_list.ix[stock_code]['timeToMarket']), '%Y%m%d').strftime(
            '%Y-%m-%d')

    if end_date == None:
        end_date = getNowDateToStr()

    price_df = ts.get_k_data(stock_code, ktype='D',autype=fq_type, start=start_date, end=end_date)
    param_list = zip(price_df['code'],price_df['date'],price_df['open'],price_df['close'],\
                   price_df['high'],price_df['low'],price_df['volume'])

    param_in = [(param[0],param[1],float(param[2]),float(param[3]),float(param[4]), \
                 float(param[5]),int(param[6])) for param in param_list]


    sql_insert = "insert into stock_price_day(s_code,s_date,s_open,s_close,s_high,s_low,s_volume)" \
                " values (%s,%s,%s,%s,%s,%s,%s)"

    num_insert = execute_many_to_db(sql_insert,param_in,cursor)
    if num_insert is None:
        num_insert = 0

    print "%d rows of code %s are insert into database!" %(num_insert,stock_code)


if __name__=='__main__':
#update_price_by_stockcode('600783')
    conn,cursor = generate_db_link('192.168.0.105', '3306', 'stock_user', 'Ws143029', 'stock_database')
    update_price_by_stocks_combination(Series(['603000','601898']),fqtype='qfq',cursor=cursor)
    #insert_stock_data_by_code('600372', start_date='2016-07-14', end_date='2016-12-23', cursor=cursor)