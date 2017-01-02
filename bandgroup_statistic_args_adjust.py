from numpy import arange
from pandas import DataFrame,Series
from statistics_stock_band_calculate import get_prices_by_stock_code
from itertools import product
from common_tools import get_interval_by_begin_end_date
from db_tools import generate_db_link,close_db_link
from band_group_statistic import insert_alldata_of_bandgroup_to_db

#max_hold_duration_dict:key:'day','trade'   value:(start,end,step)
def arguments_init(threshold_start,threshold_end,threshold_step,max_hold_duration_dict):

    threshold_args = arange(threshold_start,threshold_end,threshold_step)
    max_hold_duration_range_dict = {hold_type:arange(start,end,step) for hold_type,(start,end,step) \
                              in  max_hold_duration_dict.iteritems()}

    max_hold_duration_iter_dict = Series([(threshold_item,max_duration_iten,hold_type) for hold_type,max_range_ary\
                                          in max_hold_duration_range_dict.iteritems()
                                   for threshold_item,max_duration_iten in product(threshold_args,max_range_ary)])

    #print threshold_args
    #print max_hold_duration_iter_dict
    #args_combine = product(threshold_args,max_hold_duration_args,hold_type_list)
    #args_output = Series([args for args in args_combine])

    return max_hold_duration_iter_dict

def do_statistic_by_arguments_adjust(stock_code,start_date,end_date,group_type,threshold_start,threshold_end,threshold_step, \
                                     max_hold_duration_dict,cursor):
    args_combine = arguments_init(threshold_start,threshold_end,threshold_step,max_hold_duration_dict)
    interval, start_date, end_date = get_interval_by_begin_end_date(start_date, end_date)

    #price_datas = get_prices_by_stock_code(stock_code, cursor, interval)
    for threshold,max_hold_duration,hold_type  in args_combine:
        insert_alldata_of_bandgroup_to_db(stock_code, threshold, group_type, start_date, end_date, hold_type, \
                                          max_hold_duration, cursor)

if __name__ == '__main__':
    conn, cursor = generate_db_link('192.168.0.105', '3306', 'stock_user', 'Ws143029', "stock_database")
    do_statistic_by_arguments_adjust('600019','2013-01-01','2016-01-01','H',0.05,1.0,0.01, \
                                     {"day": (1, 90, 1), "trade": (1, 60, 1)},cursor)

    close_db_link(conn, cursor)
    """
    args_combine = arguments_init(0.05,0.1,0.001,5,60,1,['day','trade'])
    print len(args_combine)
    for args in args_combine:
        for a in args:
            print a
    """