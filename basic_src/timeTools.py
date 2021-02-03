#!/usr/bin/env python
# Filename: timeTools 
"""
introduction: functions and classes to handle datetime

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 29 December, 2020
"""

import os,sys
import basic_src.basic as basic

from datetime import datetime
from dateutil.parser import parse
import re

def get_yeardate_yyyymmdd(in_string):
    '''
    get datetime object from a filename (or string)
    Args:
        in_string: input string containing yyyymmdd

    Returns: datetime

    '''
    pattern = '[0-9]{8}'
    format = '%Y%m%d'
    found_strs = re.findall(pattern,in_string)
    if len(found_strs) < 1:
        basic.outputlogMessage('Warning, cannot found yyyymmdd string in %s'%(in_string))
        return None
    # for str in found_strs:
    #     print(str)
    #     date_obj = parse(str,yearfirst=True)
    #     print(date_obj)

    datetime_list = []
    for str in found_strs:
        try:
            date_obj = datetime.strptime(str, format)
            # print(date_obj)
            datetime_list.append(date_obj)
        except ValueError as e:
            # print(e)
            pass

    # print(datetime_list)
    if len(datetime_list) != 1:
        basic.outputlogMessage('Warning, found %d yyyymmdd string in %s' % (len(datetime_list), in_string))
        return None
    return datetime_list[0]

def str2date(date_str,format = '%Y%m%d'):
    date_obj = datetime.strptime(date_str, format)
    return date_obj

def date2str(date, format='%Y%m%d'):
    return date.strftime(format)

def diff_yeardate(in_date1, in_date2):
    '''
    calculate the difference between two date
    Args:
        in_date1:
        in_date2:

    Returns: absolute of days

    '''
    diff = in_date1 - in_date2
    # print(diff)
    diff_days = diff.days + diff.seconds / (3600*24)
    # print(diff_days)
    return abs(diff_days)


def test():
    # out = get_yeardate_yyyymmdd('20170301_10300100655B5A00_1030010066B4AA00.tif')
    out = get_yeardate_yyyymmdd('20201230_10300100655B5A00_1030010066B4AA00.tif')
    print(out)
    diffdays = diff_yeardate(out,datetime.now())
    print(diffdays)


if __name__=='__main__':
    test()
    pass