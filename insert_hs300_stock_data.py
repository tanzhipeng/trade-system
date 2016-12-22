import insert_stock_price_day
import tushare as ts


def insert_hs300_stock_data():
    hs300_list = ts.get_hs300s()['code']
    insert_stock_price_day.insert_price_by_stocks_combination(hs300_list)

def update_hs300_stock_data():
    hs300_list = ts.get_hs300s()['code']
    insert_stock_price_day.update_price_by_stocks_combination(hs300_list)

if __name__ == '__main__':
    update_hs300_stock_data()