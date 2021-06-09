import json
import fmla_dao as dao
import fmla_config as conf
from botocore.exceptions import ClientError


def lambda_handler(event, context):
    employeeId = event['queryStringParameters']['id']
    year = event['queryStringParameters']['year']
    
    #employeeId = '1002'
    #year = '2022'
    
    table = dao.get_client_table()
    
    responseData = {}
    responseObject = {}
    responseObject['headers'] = {}
    responseObject['headers']['Content-Type'] = 'application/json'
    responseObject['headers']['Access-Control-Allow-Origin'] = '*'

    try:
        employeeData = dao.get_employee_data(table, conf.get_eid_key(), employeeId)
        totalUsed = 0
        try:
            totalUsed = employeeData[conf.get_leave_by_year()][year][conf.get_hours_used_key()]
        except KeyError:
            print('Year key does not exist in map. Setting hours used to 0')
        
        responseData['employeeId'] = employeeId
        responseData['year'] = year
        responseData['hoursUsed'] = int(totalUsed)
        hoursAvailable = conf.get_fmla_limit() - int(totalUsed)
        responseData['hoursAvailable'] = hoursAvailable
        
        '''
        eventHistory = []
        for e in yearlyData['requested']:
            eventData = EventData(e['start'], e['end'], e['accepted'], e['hours'])
            print(e)
            eventHistory.append(eventData)
        #responseData['eventHistory'] = eventHistory
        '''
        
        responseObject['body'] = json.dumps(responseData)
        responseObject['statusCode'] = 200
        return responseObject
    except ClientError as e:
        print('client error')
        print(e.response['Error']['Message'])
        responseObject['error']=e.response['Error']['Message']
        return responseObject
    else:
        return responseObject
