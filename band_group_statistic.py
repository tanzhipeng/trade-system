#coding=utf-8
import common_tools
import statistics_stock_band_calculate
from common_tools import get_day_num_by_date_range,get_interval_by_begin_end_date
from statistics_stock_band_calculate import get_interval_by_begin_end_date,get_price_band_and_groups_by_prices,\
    insert_bandgroup_of_stock_to_db
from pandas import Series,DataFrame
from db_tools import generate_db_link





def insert_alldata_of_bandgroup_to_db(stock_code,threshold,group_type,start_date,end_date=None,hold_type=None,\
    max_hold_duration=None,cursor=None):
    statistic_data, band_group_list, price_datas = get_all_data_on_bandgroup(stock_code,threshold,group_type, \
        start_date,end_date,hold_type,max_hold_duration,cursor=cursor)

    band_group_list1,price_datas1,group_info_id = insert_bandgroup_of_stock_to_db(stock_code, start_date, end_date,\
        group_type, threshold, hold_type, max_hold_duration, cursor, price_datas, band_group_list)





def insert_bandgroup_statistic_to_db(stock_code,group_info_id,statistic_data):




#stock_code:股票编码  threshold_h:上涨波段阀值    threshold_l：下跌波段阀值
#begin：股价起始区间   end_date:股价结束区间  hold_type：最长持股周期单位（day:按自然日  其他:按交易日）  max_hold_duration:最大持股周期
def get_all_data_on_bandgroup(stock_code,threshold,group_type,start_date,end_date=None,hold_type=None,\
    max_hold_duration=None,cursor=None):

    interval,start_date,end_date = get_interval_by_begin_end_date(start_date,end_date)
    band_group_list = None
    price_datas = None
    statistic_data = None

    bandgroup_statistic_data_dict = {"band_num":[],"group_duration_trade":[],"group_duration_date":[],\
                                  "duration_betwn_prev_trade":[],"duration_betwn_prev_date":[],\
                                  "max_reverse_ratio":[],"price_ratio":[]
                                  }

    band_group_list, price_datas = get_price_band_and_groups_by_prices(stock_code, threshold, group_type,interval,\
                                       'day', 30, cursor=cursor)

    if threshold is not None:
        for band_group in band_group_list:
            get_statics_data_by_bandgrouplist(band_group,band_group_list,price_datas,bandgroup_statistic_data_dict)


        bandgroup_dataframe = DataFrame(bandgroup_statistic_data_dict)
        statistic_data = do_statistic_on_bandgroup(bandgroup_dataframe)

    return statistic_data,band_group_list,price_datas

def get_statics_data_by_bandgrouplist(band_group,band_group_list,price_datas,bandgroup_statistic_data_dict):

    duration_betwn_prev_trade = 0
    duration_betwn_prev_date = 0

    #start_date = band_group['start_date']
    #end_date = band_group['end_date']
    band_num = band_group['band_num']
    group_duration_trade = band_group['group_duration_trade']
    group_duration_date = band_group['group_duration_date']
    price_ratio = band_group['price_ratio']
    max_reverse_ratio = band_group['max_reverse_ratio']


    band_group_index = band_group_list.index(band_group)

    if band_group_index >= 1:
        last_band_group = band_group_list[band_group_index-1]
        startdate_last_bandgroup = last_band_group['start_date']
        startdate_current_bandgroup = band_group['start_date']

        duration_betwn_prev_trade = price_datas['s_date'][startdate_last_bandgroup:startdate_current_bandgroup].count()
        duration_betwn_prev_date = get_day_num_by_date_range(startdate_current_bandgroup-startdate_last_bandgroup)

    elif band_group_index == 0:
        duration_betwn_prev_trade=0
        duration_betwn_prev_date=0
    else:
        return None

    bandgroup_statistic_data_dict['band_num'].append(band_num)
    bandgroup_statistic_data_dict['group_duration_trade'].append(group_duration_trade)
    bandgroup_statistic_data_dict['group_duration_date'].append(group_duration_date)
    bandgroup_statistic_data_dict['duration_betwn_prev_trade'].append(duration_betwn_prev_trade)
    bandgroup_statistic_data_dict['duration_betwn_prev_date'].append(duration_betwn_prev_date)
    bandgroup_statistic_data_dict['max_reverse_ratio'].append(max_reverse_ratio)
    bandgroup_statistic_data_dict['price_ratio'].append(price_ratio)

    #print bandgroup_statistic_data_dict['band_num']


def do_statistic_on_bandgroup(bandgroup_dataframe):

    #print bandgroup_dataframe
    #print bandgroup_dataframe.values

    statistic_data = bandgroup_dataframe.apply(do_statistic_on_series,axis=0)
    return statistic_data


def do_statistic_on_series(column):
    qtl_5_percnt, qtl_10_percnt, qtl_15_percnt, qtl_20_percnt, qtl_30_percnt, qtl_70_percnt, \
    qtl_75_percnt, qtl_80_percnt, qtl_85_percnt, qtl_90_percnt = do_quantile_with_column(column)

    return Series([column.mean(),column.std(),column.median(),column.min(),qtl_5_percnt,qtl_10_percnt,qtl_15_percnt,qtl_20_percnt,qtl_30_percnt,qtl_70_percnt,
                   qtl_75_percnt,qtl_80_percnt,qtl_85_percnt,qtl_90_percnt,column.max()],index=['mean','std','median','min','qtl_5_percnt',\
                    'qtl_10_percnt', 'qtl_15_percnt','qtl_20_percnt','qtl_30_percnt',\
                    'qtl_70_percnt','qtl_75_percnt','qtl_80_percnt',\
                    'qtl_85_percnt','qtl_90_percnt','max'])

def do_quantile_with_column(column):
    qtl_5_percnt,qtl_10_percnt,qtl_15_percnt,qtl_20_percnt,qtl_30_percnt,qtl_70_percnt,\
    qtl_75_percnt,qtl_80_percnt,qtl_85_percnt,qtl_90_percnt = column.quantile([.05,.10,.15,.20,.30,.70,.75,.80,.85,.90])

    return qtl_5_percnt,qtl_10_percnt,qtl_15_percnt,qtl_20_percnt,qtl_30_percnt,qtl_70_percnt,\
    qtl_75_percnt,qtl_80_percnt,qtl_85_percnt,qtl_90_percnt









if __name__ == '__main__':
    #interval = get_interval_by_begin_end_date('2014-01-01', '2016-08-18')
    #h_band_group_list, price_datas = get_price_band_and_groups_by_prices('000503', 0.10, 'H',interval, 'day', 30)
    conn, cursor = generate_db_link('192.168.0.105', '3306', 'stock_user', 'Ws143029', "stock_database")
    statistic_data,band_group_list,price_datas = get_all_data_on_bandgroup('600019',0.10,'H','2016-01-01','2016-07-01','trade',20,cursor)

    print statistic_data
    #print type(statistic_data)
    #print statistic_data.columns
    #print statistic_data.values

    #print statistic_data.columns
    #print statistic_data.values
    """
    for static_data in bandgroup_statistic_data_list:


            'group_duration_trade:',static_data['group_duration_trade'],'group_duration_date:',static_data['group_duration_date'],\
        'duration_between_previous_trade:', static_data['duration_between_previous_trade'],'duration_between_previous_date:', static_data['duration_between_previous_date'],\
        'max_reverse_ratio:', static_data['max_reverse_ratio'],'price_ratio:', static_data['price_ratio']

    """

    """
    for group in h_band_group_list:
        get_statics_data_by_bandgrouplist(group, h_band_group_list, price_datas, bandgroup_statistic_data_list)

        for line in bandgroup_statistic_data_list:
            print "band_group_id:", line['band_group_id'], "band_num:", line['band_num'], "group_duration_trade:", line[
                'group_duration_trade'], "group_duration_date:", line['group_duration_date'], \
                "duration_between_previous_trade:", line[
                'duration_between_previous_trade'], "duration_between_previous_date:", line[
                'duration_between_previous_date'], \
                "max_reverse_ratio:", line['max_reverse_ratio'], "price_ratio:", line['price_ratio']
    """