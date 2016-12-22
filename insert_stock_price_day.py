import pymysql
import tushare as ts
import datetime


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

def update_price_by_stocks_combination(stocks_code,autype='qfq'):
    stock_base_list = ts.get_stock_basics()
    conn = pymysql.connect(host='192.168.0.103', unix_socket='3306', user='stock_user', passwd='Ws143029')
    cursor = conn.cursor()
    cursor.execute("use stock_database")

    ##try:

    for code in stocks_code:
        update_price_by_stockcode(code,cursor,stock_base_list,autype)
        cursor.connection.commit()
    ##except Exception,e:
        ##print('There is something wrong when update price data :%s',str(e))
    ##finally:
    cursor.close()
    conn.close()

def update_price_by_stockcode(stock_code,cursor,stock_base_list,autype='qfq'):


    cursor.execute('SELECT MAX(s_date) FROM stock_price_day WHERE s_code = %s',(stock_code,))

    latest_date = cursor.fetchone()[0]

    if latest_date is not None:

        latest_date_str = latest_date.strftime('%Y-%m-%d')
        now_date_str = getNowDate()

        if latest_date_str != now_date_str:
            start_date_str = latest_date.replace(day=latest_date.day+1).strftime('%Y-%m-%d')
            df = ts.get_h_data(stock_code,start=start_date_str,end=now_date_str)
            if df is not None:
                insert_price_by_stockcode(stock_code,cursor,stock_base_list,start_date=start_date_str,end_date=now_date_str,autype=autype)
    else:
        insert_price_by_stockcode(stock_code,cursor,stock_base_list,autype=autype)


#insert the price data of the combination of stocks to the database
#The input argument is sequence which contain the code of stocks
def insert_price_by_stocks_combination(stocks_code,autype='qfq'):

    stock_base_list = ts.get_stock_basics()

    conn = pymysql.connect(host='192.168.0.103', unix_socket='3306', user='stock_user', passwd='Ws143029')
    cursor = conn.cursor()
    cursor.execute("use stock_database")


    for code in stocks_code:
        insert_price_by_stockcode(code,cursor,stock_base_list,autype=autype)
        cursor.connection.commit()

    cursor.close()
    conn.close()

#insert daily price of a stock into database
def insert_price_one_day(price,code,cursor):
    cursor.execute(
        "insert into stock_price_day(s_code,s_date,s_open,s_high,s_low,s_close,s_volume,s_amount) values (%s,%s,%s,%s,%s,%s,%s,%s)",
        (code, price.trade_date, price.open, price.high, price.low,price.close, price.volume ,price.amount))

#insert price of a stock whith a period into database
def insert_price_by_stockcode(stock_code,cursor,stock_base_list,start_date=None,end_date=None,fq_type=None,autype='qfq'):
    #stock_base_list = None
    if start_date==None:
        #stock_base_list = ts.get_stock_basics()
        #print(type(stock_base_list.ix[stock_code]['timeToMarket']))
        #start_date = str(datetime.datetime.strptime(str(stock_base_list.ix[stock_code]['timeToMarket']), '%Y%m%d'))
        start_date = datetime.datetime.strptime(str(stock_base_list.ix[stock_code]['timeToMarket']), '%Y%m%d').strftime('%Y-%m-%d')
    if end_date==None:
        end_date = getNowDate()

    price_df = ts.get_h_data(stock_code,start=start_date,end=end_date,autype=autype)
    price_df['trade_date'] = price_df.index.strftime('%Y%m%d')
    price_df.apply(insert_price_one_day,args=(stock_code,cursor),axis=1)


#return the today with the format 'yyyy-mm-dd'
def getNowDate():
    now = datetime.datetime.now()
    now_str = now.strftime("%Y-%m-%d")
    return now_str


if __name__=='__main__':
#update_price_by_stockcode('600783')
    insert_price_by_stocks_combination(['600018'],autype='None')