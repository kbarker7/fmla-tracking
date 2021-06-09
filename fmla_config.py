#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  8 20:21:30 2021

@author: kevinbarker
"""

from datetime import date

#Config methods

def get_dynamodb_name():
    return 'dynamodb'

def get_table_name():
    return 'employee-fmla-tracking-table'

def get_holidays():
    holidays = ['2021-01-01', '2021-01-18', '2021-02-15', '2021-05-31', '2021-07-05',
                    '2021-08-06', '2021-10-11', '2021-11-11', '2021-11-25', '2021-12-24',
                    '2021-12-31', '2022-01-17', '2022-02-21', '2022-05-30', '2022-07-04',
                    '2022-10-10', '2022-11-11', '2022-11-24', '2022-12-26', '2023-01-02']
    return holidays

def get_date_input_format():
    return '%Y-%m-%d'

def get_date_format():
    return '%m/%d/%Y'

def get_fmla_approved_text():
    return 'FMLA Approved for request leave.'

def get_fmla_partial_text():
    return 'Time requested is only able to be partially approved. Please resubmit request within time constraints'

def get_fmla_denied_text():
    return 'FMLA Denied. No more available time for requested calendar year.'

def get_eid_key():
    return 'employeeId'

def get_leave_by_year():
    return 'leaveByYear'

def get_hours_used_key():
    return 'totalHoursUsed'

def get_requested_key():
    return 'requested'

def get_week_hours():
    return 40

def get_fmla_limit():
    return 12 * get_week_hours()

def get_final_date_of_year(year):
    return date(year, 12, 31)

def get_first_date_of_year(year):
    return date(year, 1, 1)