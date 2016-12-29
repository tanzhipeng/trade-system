from numpy import arange
from pandas import DataFrame,Series
from statistics_stock_band_calculate import get_prices_by_stock_code
from itertools import product
from common_tools import get_interval_by_begin_end_date

def arguments_init(threshold_start,threshold_end,threshold_step,max_hold_duration_start,max_hold_duration_end, \
                    max_hold_duration_step,hold_type_list):

    threshold_args = arange(threshold_start,threshold_end,threshold_step)
    max_hold_duration_args = range(max_hold_duration_start,max_hold_duration_end,max_hold_duration_step)

    args_combine = product(threshold_args,max_hold_duration_args,hold_type_list)
    args_output = Series([args for args in args_combine])

    return args_output

def do_statistic_by_arguments_adjust(stock_code,start_date,end_date,threshold_type,threshold_start,threshold_end,threshold_step,\
                          hold_type_list,max_hold_duration_start,max_hold_duration_end,max_hold_duration_step,cursor
                          ):
    args_combine = arguments_init(threshold_start,threshold_end,threshold_step,max_hold_duration_start,\
                                  max_hold_duration_end,max_hold_duration_step,hold_type_list)
    interval, start_date, end_date = get_interval_by_begin_end_date(start_date, end_date)

    price_datas = get_prices_by_stock_code(stock_code, cursor, interval)




if __name__ == '__main__':
    args_combine = arguments_init(0.05,0.1,0.001,5,60,1,['day','trade'])
    print len(args_combine)
    for args in args_combine:
        for a in args:
            print a