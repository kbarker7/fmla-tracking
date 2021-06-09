#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  8 20:22:19 2021

@author: kevinbarker
"""
from datetime import datetime, timedelta, date
import fmla_config as c
import fmla_model as m
import fmla_dao as d

#Helper Methods

def do_dates_overlap(parsedDate, yearlyData):
    list_of_requests = yearlyData[c.get_requested_key()]
    for req in list_of_requests:
        if req['accepted']:
            acceptedStart = datetime.date(datetime.strptime(req['start'], c.get_date_format()))
            acceptedEnd = datetime.date(datetime.strptime(req['end'], c.get_date_format()))
            if acceptedStart <= parsedDate <= acceptedEnd:
                print('overlap found for ' + str(parsedDate) + ' between date ' + str(acceptedStart) + ' - ' + str(acceptedEnd))
                return True
    return False

def dates_are_same_year(startDate, endDate):
    if startDate.year != endDate.year:
        print('Dates are over several years')
        differenceInYears = endDate.year - startDate.year
        if differenceInYears > 1:
            raise ValueError('Invalid request. Dates span more than 1 calendar year')
        return False
    else:
        return True

def get_leave_by_year_data(employeeData, year, eid, table):
    try:
        return employeeData[c.get_leave_by_year()][year]
    except KeyError:
        d.insert_new_leave_year(eid, year, table)
        return get_leave_by_year_data(d.get_employee_data(table, c.get_eid_key(), eid), year, eid, table)

def get_datetime_for_input(inputDate, isStartDate):
    inputDate = datetime.date(datetime.strptime(inputDate, c.get_date_input_format()))
    holidays = c.get_holidays()
    today_date = date.today()
    if isStartDate:
        if inputDate < today_date:
            inputDate = today_date
        if inputDate.isoweekday() > 5:
            inputDate = inputDate + timedelta(8 - inputDate.isoweekday())
            #print('Start date is on a weekend, advancing request forward to on next weekday')
        if inputDate in holidays:
            inputDate = inputDate + inputDate(days=1)
            #print('Start date is a holiday, advancing request one day forward')
    else:
        if inputDate < today_date:
            raise ValueError('Invalid end date passed in')
        if inputDate.isoweekday() > 5:
            inputDate = inputDate - timedelta(inputDate.isoweekday()%5)
            #print('End date is on a weekend, advancing request back to on last weekday')
        if inputDate in holidays:
            inputDate = inputDate - timedelta(days=1)
            #print('End date is a holiday, advancing request one day back')
    return inputDate

'''
#PARTIAL ACCEPTANCE BUG
If request contains holiday, and is partially accepted, 
possible for final day of leave to fall on that holiday
'''
def create_partial_acceptance(getAcceptedObject, inputStartDate, inputEndDate, hours):
    days = int(hours/8)
    date_range = []
    maxLengthToParse = inputEndDate - inputStartDate
    if getAcceptedObject:
        for day in range(maxLengthToParse.days + 1):
            newDate = inputStartDate + timedelta(days=day)
            if (newDate.isoweekday() <= 5):
                date_range.append(newDate)
                if days == len(date_range):
                    break
        eventData = m.EventData(inputStartDate.strftime(c.get_date_format()), date_range[-1].strftime(c.get_date_format()), True, hours)
        return eventData
    else:
        for day in range(maxLengthToParse.days + 1):
            newDate = inputEndDate - timedelta(days=day)
            if (newDate.isoweekday() <= 5):
                date_range.append(newDate)
                if days == len(date_range):
                    break
        eventData = m.EventData(date_range[-1].strftime(c.get_date_format()), inputEndDate.strftime(c.get_date_format()), False, hours)
        return eventData

def get_requested_hours(parsedStartDate, parsedEndDate):
    if parsedEndDate < parsedStartDate:
        raise ValueError('Selected end date is before selected start date')
    
    requested_time_length = parsedEndDate-parsedStartDate
    requested_dates = []
    for i in range(requested_time_length.days + 1):
        newDate = parsedStartDate + timedelta(days=i)
        if (newDate.isoweekday() <= 5):
            requested_dates.append(newDate)
    
    hours = len(requested_dates) * 8
    return hours

def check_time_available(fmlaLimit, timeUsed, timeRequested):
    if timeUsed + timeRequested <= fmlaLimit:
        acceptedHours = timeUsed + timeRequested
        remainingHours = fmlaLimit - acceptedHours
        return m.AvailabilityObject(True, False, timeRequested, timeRequested, 0, acceptedHours, remainingHours, c.get_fmla_approved_text())
    else:
        if timeUsed < fmlaLimit:
            difference = timeUsed + timeRequested - fmlaLimit
            acceptedTime = timeRequested - difference
            return m.AvailabilityObject(False, True, timeRequested, acceptedTime, difference, fmlaLimit, 0, c.get_fmla_partial_text())
        else:
            return m.AvailabilityObject(False, False, timeRequested, 0, timeRequested, fmlaLimit, 0, c.get_fmla_denied_text())

def handle_results(eid, year, availabilityObject, parsedStartDate, parsedEndDate, table):
    if availabilityObject.fmlaAccepted and not availabilityObject.partialAcceptance:
        eventData = m.EventData(parsedStartDate.strftime(c.get_date_format()), parsedEndDate.strftime(c.get_date_format()), True, availabilityObject.acceptedHours)
        d.update_time_available(eid, year, availabilityObject.totalHoursUsed, table)
        d.insert_time_request(eid, year, eventData, table)
    elif availabilityObject.partialAcceptance:
        #acceptedEvent = create_partial_acceptance(True, parsedStartDate, parsedEndDate, availabilityObject.acceptedHours)
        #deniedEvent = create_partial_acceptance(False, parsedStartDate, parsedEndDate, availabilityObject.deniedHours) 
        eventData = m.EventData(parsedStartDate.strftime(c.get_date_format()), parsedEndDate.strftime(c.get_date_format()), False, availabilityObject.requestedHours)
        #d.update_time_available(eid, year, availabilityObject.totalHoursUsed, table)
        #d.insert_time_request(eid, year, acceptedEvent, table)
        #d.insert_time_request(eid, year, deniedEvent, table)
        d.insert_time_request(eid, year, eventData, table)
    else:
        eventData = m.EventData(parsedStartDate.strftime(c.get_date_format()), parsedEndDate.strftime(c.get_date_format()), False, availabilityObject.requestedHours)
        d.insert_time_request(eid, year, eventData, table)

def create_joint_availability_object(startObject, startYear, endObject, endYear):
    startMessage = 'For calendar year ' + startYear + ', '
    endMessage = '. For calendar year ' + endYear + ', '
    period = '.'
    requestedHours = startMessage + str(startObject.requestedHours) + endMessage + str(endObject.requestedHours) + period
    acceptedHours = startMessage + str(startObject.acceptedHours) + endMessage + str(endObject.acceptedHours) + period
    deniedHours = startMessage + str(startObject.deniedHours) + endMessage + str(endObject.deniedHours) + period
    totalHoursUsed = startMessage + str(startObject.totalHoursUsed) + endMessage + str(endObject.totalHoursUsed) + period
    remainingdHours = startMessage + str(startObject.remainingHours) + endMessage + str(endObject.remainingHours) + period
    message = startMessage + startObject.message + endMessage + endObject.message + period
    fmlaAccepted = startMessage + str(startObject.fmlaAccepted) + endMessage + str(endObject.fmlaAccepted) + period
    partial = startMessage + str(startObject.partialAcceptance) + endMessage + str(endObject.partialAcceptance) + period
    return m.AvailabilityObject(fmlaAccepted, partial, requestedHours, acceptedHours, deniedHours, totalHoursUsed, remainingdHours, message)
