import insert_stock_price_day
import tushare as ts
from db_tools import generate_db_link,execute_many_to_db,select_from_db


def insert_hs300_stock_data(cursor):
    hs300_list = ts.get_hs300s()['code']
    insert_stock_price_day.insert_price_by_stocks_combination(stocks_code_series=hs300_list,cursor=cursor)

def update_hs300_stock_data():
    hs300_list = ts.get_hs300s()['code']
    insert_stock_price_day.update_price_by_stocks_combination(stocks_code_series=hs300_list)

if __name__ == '__main__':
    conn, cursor = generate_db_link('192.168.0.105', '3306', 'stock_user', 'Ws143029', 'stock_database')
    insert_hs300_stock_data(cursor)