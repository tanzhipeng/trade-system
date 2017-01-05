import pandas as pd
from datetime import date,datetime

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

def get_day_num_by_date_range(date_timedelta):
    #print type(date_range)
    #return float(date_range.total_seconds()/(24*60*60))
    #print date_timedelta.days
    return date_timedelta.days


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
    print "end_index:",end_index

    begin_index = 0
    if (end_index+1) > day_num:
        begin_index = end_index - (day_num-1)
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

def getNowDateToStr():
    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d")
    return now_str


def float_range(start,end,step):
    output_list = []
    if end > start:
        now = start
        output_list.append(start)
        while (now+step)<=end:
            now = now+step
            output_list.append(now)


    else:
        output_list.append(start)

    return output_list

if __name__ == '__main__':
    print float_range(0.05,0.5,0.001)