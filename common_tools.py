import pandas as pd
from datetime import date

def get_interval_by_begin_end_date(begin_date,end_date=None):

    if begin_date is not None:

        if end_date is not None:
            interval = pd.date_range(begin_date, end_date, freq='D')
        else:
            end_date = date.today().strftime()
            interval = pd.date_range(begin_date, end_date, freq='D')

        return interval
    else:
        return None

def get_day_num_by_date_range(date_range):
    return float(date_range.total_seconds()/(24*60*60))


def get_index_within_datetime_interval(dtime,datetime_interval):
    #list_datetime_interval = list(datetime_interval)

    index_datetime = datetime_interval.get_loc(dtime)
    #index_datetime = list_datetime_interval.index(dtime)

    return index_datetime

def get_datetime_by_index_within_interval(index,datetime_interval):
    list_datetime_interval = list(datetime_interval)
    dtime = list_datetime_interval[index]

    return dtime


#data_index:the datetime-index
#day_num:the number of days between the begin date and end date
def get_begindate_from_enddate(end_date,date_index,day_num):

    datetime_interval = date_index

    end_index = get_index_within_datetime_interval(end_date,datetime_interval)
    begin_index = 0
    if end_index >= day_num:
        begin_index = end_index - day_num
    else:
        begin_index = 0

    begin_date = get_datetime_by_index_within_interval(begin_index,datetime_interval)

    #price_array_interval = price_array[begin_index:end_index]
    return begin_date

#get the date_interval by begin and end date
def get_interval_by_begin_end_date(start_date,end_date=None):

    if start_date is not None:

        if end_date is not None:
            interval = pd.date_range(start_date, end_date, freq='D')
        else:
            end_date = date.today().strftime()
            interval = pd.date_range(start_date, end_date, freq='D')

        return interval,start_date,end_date
    else:
        return None

