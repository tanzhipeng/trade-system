#coding=utf-8
import pymysql
import tushare as ts
import pandas as pd
import numpy as np
from pandas import DataFrame,Series
from datetime import date
from pandas.tseries.offsets import Day, BusinessMonthBegin,BusinessMonthEnd,BQuarterBegin,BQuarterEnd,BYearBegin,BYearEnd,BusinessDay
from common_tools import get_index_within_datetime_interval,get_datetime_by_index_within_interval,\
get_day_num_by_date_range,get_begindate_from_enddate,get_interval_by_begin_end_date
from db_tools import generate_db_link,close_db_link,execute_single_to_db,execute_many_to_db,select_from_db

#instance definition:
#(1)price_band:
#datatype:dict
#columns: band_id,start_date,end_date,seq_num,price_start,price_end,price_raio,band_type(H,L),trade_date_list,duration,band_group_id
#(2)band_group:
#datatype:list of dict
#columns: band_group_id,start_date,end_date,price_start,price_end,seq_num,price_ratio,group_type,group_duration,band_list

def insert_bandgroup_of_stock_to_db(stock_code,start_date,end_date,group_type,threshold,\
                                    cursor,hold_type=None,max_hold_duration=None,price_datas=None):

    interval,start_date,end_date = get_interval_by_begin_end_date(start_date, end_date)
    band_group_list, price_datas = get_price_band_and_groups_by_prices(stock_code, threshold, group_type, interval, hold_type, max_hold_duration,
                                                                         price_datas, cursor)

    group_num = len(band_group_list)

    insert_bandgroup_info_to_db(stock_code, start_date, end_date, group_type, threshold, hold_type, max_hold_duration, group_num, cursor)
    group_info_id = int(cursor.lastrowid)

    insert_bandgroup_data_to_db(stock_code, group_info_id, band_group_list, cursor)

    return band_group_list,price_datas

def insert_bandgroup_info_to_db(stock_code,start_date,end_date,group_type,threshold,hold_type,max_hold_duration,group_num,cursor):

    param_in = [stock_code,start_date,end_date,group_type,threshold,hold_type,max_hold_duration,group_num]

    sql_insert = "insert into stock_band_group_info(s_code,start_date,end_date,group_type,threshold,\
                hold_type,max_hold_duration,group_num,create_date,refresh_date) values (\
                %s,%s,%s,%s,%s,%s,%s,%s,now(),now())"

    execute_single_to_db(sql_insert,param_in,cursor)

def insert_bandgroup_data_to_db(stock_code,group_info_oid,band_group_list,cursor):
    param_bandgroup = [[stock_code,group_info_oid,dict_group['band_group_id'], \
                        dict_group['band_num'],float(dict_group['price_ratio']),float(dict_group['max_reverse_ratio']), \
                        dict_group['group_duration_trade'],dict_group['group_duration_date'], \
                        dict_group['seq_num'],dict_group['start_date'],dict_group['end_date'], \
                        float(dict_group['price_start']),float(dict_group['price_end'])\
                        ] for dict_group in band_group_list]

    sql_insert = "insert into stock_band_group_data values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    execute_many_to_db(sql_insert,param_bandgroup,cursor)


#return price datas of stock by the stock code
#stock_price:
#datatype:DataFrame
#index:s_date1
#columns:s_date,s_open,s_close,s_high,s_low,s_volume,s_amount
def get_prices_by_stock_code(stock_code,cursor,interval=None):

    #conn = pymysql.connect(host='192.168.0.105', unix_socket='3306', user='stock_user', passwd='Ws143029')
    #cursor = conn.cursor()
    #cursor.execute("use stock_database")
    #cursor.execute('SELECT s_date,s_close,s_open,s_high,s_low,s_volume,s_amount FROM stock_price_day WHERE s_code = %s', (stock_code,))
    select_sql = 'SELECT s_date,s_close,s_open,s_high,s_low,s_volume,s_amount FROM stock_price_day WHERE s_code = %s'
    args_in = (stock_code,)
    result_list = select_from_db(select_sql,args_in,cursor)


    #price_data = DataFrame(list(cursor.fetchall()), columns=['s_date', 's_close', 's_open','s_high','s_low','s_volume','s_amount'])
    price_data = DataFrame(result_list,columns=['s_date', 's_close', 's_open', 's_high', 's_low', 's_volume', 's_amount'])
    price_data['s_date1'] = price_data['s_date']
    price_data = price_data.set_index('s_date1')
    price_data.index = pd.DatetimeIndex(price_data.index)
    price_data = price_data.sort_index()

    if interval is not None:
        price_data = get_price_dataframe_by_interval(price_data, interval)


    return price_data


#return the bands and groups within the price interval
def get_price_band_and_groups_by_prices(stock_code,threshold,threshold_type,interval=None,hold_type=None,max_hold_duration=None,price_datas=None,cursor=None):

    #price_datas = None
    band_group_list = []

    if price_datas is None:

        if interval is not None:
            price_datas = get_prices_by_stock_code(stock_code,cursor,interval)
        else:
            price_datas = get_prices_by_stock_code(stock_code,cursor)

        price_datas.apply(calculate_price_band_and_group_by_date,args=(price_datas,threshold,threshold_type,band_group_list,hold_type,max_hold_duration),axis=1)

    else:

        price_datas.apply(calculate_price_band_and_group_by_date,args=(price_datas,threshold,threshold_type,band_group_list,hold_type,max_hold_duration),axis=1)

    return band_group_list,price_datas



#instance definition:
#point: datatype:series
#columns:s_date,s_close,s_open,s_high,s_low,s_volume,s_amount,pct_change
#(1)price_band:
#datatype:dict
#columns: band_id,start_date,end_date,seq_num,price_start,price_end,price_raio,band_type(H,L),duration_trade,duration_date,band_group_id
#(2)band_group:
#datatype:dict
#columns: band_group_id,start_date,end_date,price_start,price_end,seq_num,price_ratio,group_type,group_duration_trade,group_duration_date,band_num,band_list
#(3)band_list
#datatype:list of dict


#return"h_band_group_list,l_band_group_list
def calculate_price_band_and_group_by_date(price_current,price_datas,threshold,threshold_type,band_group_list=None,hold_type=None,max_hold_duration=None):

    if (price_current is not None) and (len(price_current)>0):
        band_seq = 0
        band_seq = 0
        band_start_date = None
        band_cal_data = None
        last_band_group = None
        current_date = price_current['s_date']
        s_close = price_current['s_close']

        if threshold is not None:
            if (band_group_list is not None) and (len(band_group_list) > 0):
                last_band_group = band_group_list[-1]
            pct_change_data = cal_band_pct_data_by_point(price_datas, last_band_group, current_date, s_close, hold_type, max_hold_duration)

            if (pct_change_data is not None) and (len(pct_change_data) > 1):
                band_points = get_band_points_by_pct_data(pct_change_data, threshold, threshold_type)
                if (band_points is not None) and (len(band_points) > 0):
                    # print h_band_points
                    band_points.apply(create_pc_band_with_group_by_single_point,args=(pct_change_data, threshold_type, threshold, price_datas, band_group_list), axis=1)
        #else:
            #print 'High band pct_change data is None!'

    else:
        return False


#compute the band and group
#h_pct_change_data:columns of price_datas add column "pct_change"
#type:'H':compute the high price_band and high band_group    'L':....
#band_group:if type equals 'H',then it is high band_group ,if type equals 'L',...
#注意是否产生两个波段组的判断是，当前节点产生的波段是否有起始节点晚于当前最新的波段组第一个波段尾节点时间，如果是，则生成新波段组，否则无新波段组产生
#def refresh_band_and_group(h_pct_change_data,band_group,type,threshold):

#create a new price band(probably new group) with a single band point and current point
def create_pc_band_with_group_by_single_point(band_point,pct_change_data,band_type,threshold,price_datas,band_group_list=None):

    current_point = pct_change_data.ix[-1]
    pct_change_data_abs = pct_change_data['pct_change'].abs()
    new_band_points = pct_change_data[pct_change_data_abs > threshold]
    last_band_group = None
    band_group_id = None
    if len(new_band_points) > 0:
        if (band_group_list is not None) and (len(band_group_list)>0):
            last_band_group = band_group_list[-1]

        is_new_group,new_band_group_id = is_new_band_group(band_point,last_band_group)
        if is_new_group :
            band_group_id = new_band_group_id
        else:
            band_group_id = get_group_id_of_band(band_point,last_band_group)

        band_id = get_band_id_of_band(last_band_group)
        #print band_point
        price_band_of_point = create_single_band_of_current_point(band_point,current_point,pct_change_data,band_id,band_group_id,band_type)
        create_or_refresh_band_group(price_band_of_point,pct_change_data,band_group_list,price_datas,is_new_group,band_group_id)

        return True
    else:
        return False

def create_or_refresh_band_group(price_band_of_point,pct_change_data,band_group_list,price_datas,is_new_group=False,new_band_group_id=None):

    if  is_new_group :
        band_list = []
        start_date = price_band_of_point['start_date']
        end_date = price_band_of_point['end_date']
        price_start = price_band_of_point['price_start']
        price_end = price_band_of_point['price_end']
        seq_num = new_band_group_id
        price_ratio = cal_pct_change_between_point(price_start,price_end)
        group_type = price_band_of_point['band_type']
        group_duration_trade = price_band_of_point['duration_trade']
        group_duration_date = price_band_of_point['duration_date']
        band_list.append(price_band_of_point)
        band_num = len(band_list)

        price_array = price_datas.ix[start_date:end_date]
        max_reverse_ratio = cal_max_reverse_ratio_by_price_datas(price_array, group_type)

        new_band_group = {'band_group_id':new_band_group_id,'start_date':start_date,'end_date':end_date,
                          'price_start':price_start,'price_end':price_end,'seq_num':new_band_group_id,
                          'price_ratio':price_ratio,'group_type':group_type,'group_duration_trade':group_duration_trade,
                          'group_duration_date':group_duration_date,'band_num':band_num,'band_list':band_list,
                          'max_reverse_ratio':max_reverse_ratio
                          }
        band_group_list.append(new_band_group)

    else:
        pct_change_data_tmp = pct_change_data.ix[:-1]

        refresh_band_group = band_group_list[-1]
        band_list = refresh_band_group['band_list']
        group_start_date = refresh_band_group['start_date']
        group_end_date = refresh_band_group['end_date']
        old_start_price = refresh_band_group['price_start']
        old_group_duration_trade = refresh_band_group['group_duration_trade']
        new_end_price = price_band_of_point['price_end']
        group_type = refresh_band_group['group_type']


        new_end_date = price_band_of_point['end_date']
        new_price_end = price_band_of_point['price_end']
        new_price_ratio = cal_pct_change_between_point(old_start_price,new_end_price)
        #new_group_duration_trade = old_group_duration_trade+price_band_of_point['duration_trade']
        new_group_duration_trade = old_group_duration_trade+len(pct_change_data_tmp.ix[group_end_date:new_end_date])

        #date_interval = get_interval_by_begin_end_date(group_start_date,new_end_date)
        new_group_duration_date = get_day_num_by_date_range(new_end_date-group_start_date)

        price_array = price_datas.ix[group_start_date:new_end_date]
        max_reverse_ratio = cal_max_reverse_ratio_by_price_datas(price_array, group_type)

        band_list.append(price_band_of_point)
        band_num = len(band_list)
        refresh_band_group['end_date'] = new_end_date
        refresh_band_group['price_end'] = new_price_end
        refresh_band_group['price_ratio'] = new_price_ratio
        refresh_band_group['band_num'] = band_num
        refresh_band_group['group_duration_trade'] = new_group_duration_trade
        refresh_band_group['group_duration_date'] = new_group_duration_date
        refresh_band_group['max_reverse_ratio'] = max_reverse_ratio

    return True

def create_single_band_of_current_point(band_point,current_point,pct_change_data,band_id,band_group_id,band_type):

    #print band_point
    price_band = {}
    #start_date = band_point['s_date']
    start_date = band_point[0]
    #end_date = current_point['s_date']
    end_date = current_point[0]
    #price_start = band_point['s_close']
    price_start = band_point[1]
    #price_end = current_point['s_close']
    price_end = current_point[1]
    seq_num = band_id
    price_ratio = cal_pct_change_between_point(price_start,price_end)
    duration_trade = len(pct_change_data.ix[start_date:end_date])

    price_array = pct_change_data.ix[start_date:end_date]
    max_reverse_ratio = cal_max_reverse_ratio_by_price_datas(price_array,band_type)


    #interval = get_interval_by_begin_end_date(start_date, end_date)
    duration_date = get_day_num_by_date_range(end_date-start_date)

    #print duration_trade,duration_date
    #print start_date,end_date
    trade_date_list = list(pct_change_data['s_date'][start_date:end_date])

    price_band = {'band_id':band_id,'start_date':start_date,'end_date':end_date,'seq_num':seq_num,'price_start':price_start,
                'price_end':price_end,'price_ratio':price_ratio,'band_type':band_type,'duration_trade':duration_trade,
                  'duration_date':duration_date,'band_group_id':band_group_id,'trade_date_list':trade_date_list,'max_reverse_ratio':max_reverse_ratio}

    return price_band

#calculate the max reverse ratio within the price_datas
def cal_max_reverse_ratio_by_price_datas(price_datas,original_direction_type):
    max_reverse_ratio = 0
    max_reverse_ratio_list = price_datas.apply(cal_max_reverse_ratio_by_point, args=(price_datas, original_direction_type), axis=1)


    if original_direction_type == 'H':
        max_reverse_ratio = max_reverse_ratio_list.min()
    else:
        max_reverse_ratio = max_reverse_ratio_list.max()

    #print original_direction_type,max_reverse_ratio
    return max_reverse_ratio

#calculate the max reverse ratio from the begining of the price_datas to the point
def cal_max_reverse_ratio_by_point(current_point,price_datas,original_direction_type):

    max_reverse_ratio = 0
    current_price = current_point['s_close']
    begin_date = price_datas.ix[0]['s_date']
    end_date = current_point['s_date']
    points_interval = price_datas.ix[begin_date:end_date]


    if len(points_interval)>1:
        pct_change_sequence = cal_pct_change_between_point_interval(points_interval['s_close'], current_price)

        if original_direction_type == 'H':
            max_reverse_ratio = pct_change_sequence[pct_change_sequence<=0].min()
        else:
            max_reverse_ratio = pct_change_sequence[pct_change_sequence>=0].max()

    return max_reverse_ratio

#calculate the percent change between the currend price and history price(price of last hight/low band/当前节点与最近一个高/低波段的正数第2个时间节点之间的价格百分比)
def cal_band_pct_data_by_point(price_datas,band_group,current_date,current_price,hold_type=None,max_hold_duration=None):

    band_cal_data = None
    pct_change_sequence = None
    start_date = None
    if (band_group is not None) and (len(band_group) > 0):
        band_trade_date_list = get_feature_of_band_within_bandgroup(band_group, -1, 'trade_date_list')
        last_band_second_date = band_trade_date_list[1]

        if hold_type is None:
            start_date = last_band_second_date
        else:

            if max_hold_duration is None:
                max_hold_duration = 0

            if hold_type == 'day':
                day_duration_num = get_day_num_by_date_range(current_date - last_band_second_date)
                if day_duration_num > max_hold_duration:
                    start_date = current_date - Day(max_hold_duration)
                else:
                    start_date = last_band_second_date
            else:
                trade_day_num = len(band_trade_date_list[last_band_second_date:current_date])
                if trade_day_num > max_hold_duration:
                    date_index = price_datas.index
                    start_date = get_begindate_from_enddate(current_date,date_index,max_hold_duration)
                else:
                    start_date = last_band_second_date

        band_cal_data = price_datas.ix[start_date:current_date]
        pct_change_sequence = cal_pct_change_between_point_interval(band_cal_data['s_close'], current_price)
        band_cal_data['pct_change'] = pct_change_sequence

    else:
        start_date = price_datas.ix[0]['s_date']
        band_cal_data = price_datas.ix[start_date:current_date]
        if len(band_cal_data) > 1:
            pct_change_sequence = cal_pct_change_between_point_interval(band_cal_data['s_close'], current_price)
            band_cal_data['pct_change'] = pct_change_sequence
        else:
            band_cal_data = None

    return band_cal_data

def get_band_id_of_band(last_band_group):

    band_id = None
    last_band_id = None
    if (last_band_group is not None) and (len(last_band_group) > 0):
        last_band_id = get_feature_of_band_within_bandgroup(last_band_group, -1, 'band_id')
    else:
        last_band_id = 0

    band_id = last_band_id + 1
    return band_id

def get_group_id_of_band(band_point,last_band_group):

    band_group_id = None
    is_new_group, new_band_group_id = is_new_band_group(band_point, last_band_group)
    if is_new_group is True:
        band_group_id = new_band_group_id
        return band_group_id
    else:
        band_group_id = last_band_group['band_group_id']
        return band_group_id

#decide is then band
def  is_new_band_group(new_band_point,band_group):

    if (new_band_point is not None) and (len(new_band_point)>0):
        #last_band = band_group[-1]
        if (band_group is not None) and (len(band_group) > 0):
            #first_band = band_group[0]
            #last_date_of_first_band_in_group = get_feature_of_band_within_bandgroup(band_group, 0, 'trade_date_list')[-1]
            last_date_of_band_group = band_group['end_date']
            if (new_band_point['s_date']>last_date_of_band_group):
                last_band_group_id = band_group['band_group_id']
                new_band_group_id = last_band_group_id+1
                return True,new_band_group_id
            else:
                return False,None
                #new_group_end_point = new_band_points[-1]
                #new_group_start_point = new_band_points[new_band_points['s_date']>last_date_of_first_band_in_group][0]
        else:
            return True,1
    else:
        return False,None

def cal_pct_change_between_point_interval(price_sequence,current_price):

    current_sequence = Series(np.zeros(len(price_sequence)))
    current_sequence = current_price
    #pct_change = cal_pct_change_between_point(price_sequence,current_sequence)
    #return pct_change
    return (current_sequence - price_sequence)/price_sequence

def cal_pct_change_between_point(point_start,point_end):
    return (point_end - point_start)/point_start

def get_band_points_by_pct_data(pct_change_data,threshold,band_type):
    band_points = None
    pct_change_data_abs = pct_change_data['pct_change'].abs()
    tmp_band_points = pct_change_data[pct_change_data_abs > threshold]

    if band_type == 'H':
        band_points = tmp_band_points[tmp_band_points['pct_change'] > 0]
    else:
        band_points = tmp_band_points[tmp_band_points['pct_change'] < 0]

    return band_points

def get_band_type_by_points(point_start,point_end):
    band_type = None
    if point_start < point_end:
        band_type = 'H'
    else:
        band_type = 'L'



#get the feature of price_band of the bandgroup  with band_index and band_key
def get_feature_of_band_within_bandgroup(band_group,band_index,band_key):

    band_list = band_group['band_list']
    if (band_list is not None) and (len(band_list)>0):
        return band_list[band_index][band_key]
    else:
        return None


#freq_type:'D':Day;  'M':Month;  'Q':Quarter;   'Y':Year
def get_price_position_within_time_frequency(end_date,price_datas,freq_type,freq_num,position_type='min-max'):

    price_end_date = price_datas['s_close'][end_date]
    offsets = None
    position = None

    if freq_type=='M':
        offsets = BusinessMonthBegin(freq_num)
    elif freq_type=='Q':
        offsets = BQuarterBegin(freq_num)
    elif freq_type=='Y':
        offsets = BYearBegin(freq_num)
    else:
        offsets = BusinessDay(freq_num)

    begin_date = end_date - offsets
    price_array = price_datas['s_close'][begin_date:end_date]

    #print price_array

    if position_type == 'min-max':
        position = get_data_position_by_min_max(price_end_date, price_array)
    else:
        position = get_data_position_by_rank(end_date, price_array)

    return position

#trade_num:trade_days
def get_price_position_within_tradedays(end_date,price_datas,trade_num,position_type='min-max'):

    price_end_date = price_datas['s_close'][end_date]
    position = None

    date_index = price_datas.index
    begin_date = get_begindate_from_enddate(end_date,date_index,trade_num)
    price_array = price_datas['s_close'][begin_date:end_date]

    #print "end_date:",end_date," price_end_date:",price_end_date
    #print "price_array:",price_array

    if position_type == 'min-max':
        position = get_data_position_by_min_max(price_end_date, price_array)
    else:
        position = get_data_position_by_rank(end_date, price_array)

    #position = get_data_position_by_min_max(price_end_date,price_array)
    return position


def get_data_position_by_min_max(data,data_array):
    min_data_array = data_array.min()
    max_data_array = data_array.max()

    #print "min_data_array:",min_data_array
    #print "max_data_array:",max_data_array

    #position = (max_data_array-data)/(max_data_array-min_data_array)
    position = (data-min_data_array) / (max_data_array - min_data_array)
    return position

def get_data_position_by_rank(price_date,data_array):

    data_sort_rank = data_array.sort_values().rank(method='min')
    data_length = data_sort_rank.count()
    seq = data_sort_rank[price_date]
    position = seq/data_length

    return position

def get_price_dataframe_by_interval(price_data,interval):

    price_data_range = price_data.ix[interval]
    price_data_range = price_data_range[price_data_range['s_date'].notnull()]

    return price_data_range




if __name__ == '__main__':
    #interval,startdate,enddate = get_interval_by_begin_end_date('2014-01-01', '2016-08-18')
    #statistic_bandgroup_data_list = []
    #price_df = get_prices_by_stock_code(600019,interval)
    conn,cursor = generate_db_link('192.168.0.105','3306','stock_user','Ws143029',"stock_database")

    insert_bandgroup_of_stock_to_db('600372', '2014-01-01', '2016-08-18', 'H', 0.10, \
                                    cursor, hold_type='day', max_hold_duration=30, price_datas=None)

    #h_band_group_list,price_datas = get_price_band_and_groups_by_prices('600372',0.10,'H',interval,'day',30,None,cursor)
    #l_band_group_list,price_datas = get_price_band_and_groups_by_prices('600372', 0.5, 'L', interval, 'day', 30, price_datas,cursor)

    #group_num_h = len(h_band_group_list)
    #group_num_l = len(l_band_group_list)

    #insert_bandgroup_info_to_db('600372','2014-01-01','2016-08-18','H',0.15,'day',30,group_num_h,cursor)
    #group_info_id_h = int(cursor.lastrowid)

    #insert_bandgroup_data_to_db('600372', group_info_id_h, h_band_group_list, cursor)
    #close_db_link(conn,cursor)

    #insert_bandgroup_info_to_db('600372', '2014-01-01', '2016-08-18', 'L', 0.5, 'day', 30, group_num_l, cursor)
    #group_info_id_l = int(cursor.lastrowid)

    #insert_bandgroup_data_to_db('600372', group_info_id_l, l_band_group_list, cursor)
    #close_db_link(conn, cursor)




    #l_band_group_list, price_datas = get_price_band_and_groups_by_prices('600019', 0.10, 'L', interval, 'day', 30,price_datas)

    #print "h_group",len(h_band_group_list)
    #print "l_group",len(l_band_group_list)

    """
    for group in l_band_group_list:

        #start_position_20 = get_price_position_within_tradedays(group['start_date'], price_datas, 480, 'min-max')
        start_position_20 = get_price_position_within_time_frequency(group['start_date'], price_datas, 'M', 3,'rank')

        print "band_goup",'band_group_id:',group['band_group_id'],'price_start:',group['price_start'],'price_end:',group['price_end'],\
            'start_date:',group['start_date'],'end_date:',group['end_date'],'group_type:',group['group_type'],'price_ratio:',group['price_ratio'], \
            'band_num:',group['band_num'],'group_duration_trade:',group['group_duration_trade'],'group_duration_date:',group['group_duration_date'],\
            'max_reverse_ratio:',group['max_reverse_ratio'],'start_position_2M:',start_position_20

    print "------------------------------------------------------------------"
    """
    """
    for group in h_band_group_list:

        start_position_20 = get_price_position_within_time_frequency(group['start_date'], price_datas, 'M', 3,'rank')

        print "band_goup", 'band_group_id:', group['band_group_id'], 'price_start:', group['price_start'], 'price_end:', group['price_end'], \
                'start_date:', group['start_date'], 'end_date:', group['end_date'], 'group_type:', group[
                'group_type'], 'price_ratio:', group['price_ratio'], \
                'band_num:', group['band_num'], 'group_duration_trade:', group[
                'group_duration_trade'], 'group_duration_date:', group['group_duration_date'], \
                'max_reverse_ratio:', group['max_reverse_ratio'], 'start_position_2M:', start_position_20
    """


    """
        price_band_list = group['band_list']
        for price_band in price_band_list:
            start_position_20 = get_price_position_within_tradedays(price_band['start_date'],price_datas,40,'min-max')

            print "price_band",'band_id:',price_band['band_id'],'price_start:',price_band['price_start'],'price_end:',price_band['price_end'],\
                'start_date:',price_band['start_date'],'end_date:',price_band['end_date'],'price_ratio:',price_band['price_ratio'],'band_type:',price_band['band_type'],\
                'duration_trade:',price_band['duration_trade'],'duration_date:',price_band['duration_date'],'max_reverse_ratio:',price_band['max_reverse_ratio'],\
                'start_position_20:',start_position_20
    """

