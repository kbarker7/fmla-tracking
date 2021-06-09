import json
from botocore.exceptions import ClientError
import fmla_config as conf
import fmla_dao as dao
import fmla_model as model
import fmla_helper as helper

def lambda_handler(event, context):
    employeeId = event['employeeId']
    startDate = event['startDate']
    endDate = event['endDate']
    availabilityObject = model.AvailabilityObject(False, False, 0, 0, 0, 0, 0, "Dummy Object")
    responseData = {}
    responseObject = {}
    responseObject['statusCode'] = 200
    responseObject['headers'] = {}
    responseObject['headers']['Content-Type'] = 'application/json'
    responseObject['headers']['Access-Control-Allow-Origin'] = '*'
    responseObject['headers']['Access-Control-Allow-Headers'] = '*'
    responseObject['headers']['Access-Control-Allow-Methods'] = '*'
    
    table = dao.get_client_table()
    try:
        parsedStartDate = helper.get_datetime_for_input(startDate, True)
        parsedEndDate = helper.get_datetime_for_input(endDate, False)
        
        #get employee data to check for overlap and ensure all years are created
        employeeData = dao.get_employee_data(table, conf.get_eid_key(), employeeId)
        startOverlap = helper.do_dates_overlap(parsedStartDate, helper.get_leave_by_year_data(employeeData, str(parsedStartDate.year), employeeId, table))
        endOverlap = helper.do_dates_overlap(parsedEndDate, helper.get_leave_by_year_data(employeeData, str(parsedEndDate.year), employeeId, table))
        if startOverlap or endOverlap:
            raise ValueError('Selected dates overlap with existing accepted request')
        
        #refresh employee data
        employeeData = dao.get_employee_data(table, conf.get_eid_key(), employeeId)
        
        if helper.dates_are_same_year(parsedStartDate, parsedEndDate):
            #print('Standard single year request')
            requestYear = str(parsedStartDate.year)
            yearlyData = helper.get_leave_by_year_data(employeeData, requestYear, employeeId, table)
            totalUsed = int(yearlyData[conf.get_hours_used_key()])
            numOfHours = helper.get_requested_hours(parsedStartDate, parsedEndDate)
            if numOfHours > 0:
                availabilityObject = helper.check_time_available(conf.get_fmla_limit(), totalUsed, numOfHours)
                helper.handle_results(employeeId, requestYear, availabilityObject, parsedStartDate, parsedEndDate, table)
                responseData['jointYear'] = False
                responseData['requestAccepted'] = availabilityObject.fmlaAccepted
                responseData['partialAcceptance'] = availabilityObject.partialAcceptance
                responseData['message'] = availabilityObject.message
                responseData['requestedHours'] = availabilityObject.requestedHours
                responseData['acceptedHours'] = availabilityObject.acceptedHours
                responseData['deniedHours'] = availabilityObject.deniedHours
                responseData['totalHoursUsed'] = availabilityObject.totalHoursUsed
                responseData['remainingHours'] = availabilityObject.remainingHours
            else:
                responseData['message'] = availabilityObject.message = 'Invalid request'
        else:
            #print('Multi Year request found')
            startYear = str(parsedStartDate.year)
            endYear = str(parsedEndDate.year)
            startYearFinalDate = conf.get_final_date_of_year(parsedStartDate.year)
            endYearBeginningDate = conf.get_first_date_of_year(parsedEndDate.year)
            numOfHoursStart = helper.get_requested_hours(parsedStartDate, startYearFinalDate)
            numOfHoursEnd = helper.get_requested_hours(endYearBeginningDate, parsedEndDate)
            
            totalUsedStart = int(helper.get_leave_by_year_data(employeeData, startYear, employeeId, table)[conf.get_hours_used_key()])
            totalUsedEnd = int(helper.get_leave_by_year_data(employeeData, endYear, employeeId, table)[conf.get_hours_used_key()])
            
            availabilityObjectStart = helper.check_time_available(conf.get_fmla_limit(), totalUsedStart, numOfHoursStart)
            availabilityObjectEnd = helper.check_time_available(conf.get_fmla_limit(), totalUsedEnd, numOfHoursEnd)
            helper.handle_results(employeeId, startYear, availabilityObjectStart, parsedStartDate, startYearFinalDate, table)
            helper.handle_results(employeeId, endYear, availabilityObjectEnd, endYearBeginningDate, parsedEndDate, table)
            availabilityObject = helper.create_joint_availability_object(availabilityObjectStart, startYear, availabilityObjectEnd, endYear)
            responseData['jointYear'] = True
            responseData['requestAccepted'] = availabilityObject.fmlaAccepted
            responseData['partialAcceptance'] = availabilityObject.partialAcceptance
            responseData['message'] = availabilityObject.message
            responseData['requestedHours'] = availabilityObject.requestedHours
            responseData['acceptedHours'] = availabilityObject.acceptedHours
            responseData['deniedHours'] = availabilityObject.deniedHours
            responseData['totalHoursUsed'] = availabilityObject.totalHoursUsed
            responseData['remainingHours'] = availabilityObject.remainingHours
              
        responseData['employeeId'] = employeeId
        responseObject['body'] = json.dumps(responseData)
        return responseObject
    except ClientError as e:
        print(e.response['Error']['Message'])
        responseData['error']=e.response['Error']['Message']
        return responseObject
    else:
        return responseObject