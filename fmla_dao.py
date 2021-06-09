#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  8 20:22:47 2021

@author: kevinbarker
"""
import boto3
from botocore.exceptions import ClientError

#DAO Methods

def get_client_table():
    client = boto3.resource('dynamodb')
    table = client.Table('employee-fmla-tracking-table')
    return table

def get_employee_data(table, key, eid):
    return table.get_item(Key={key: eid})['Item']

def update_time_available(eid, year, hoursUsed, table):
    try:
        response = table.update_item(
                Key={'employeeId': eid},
                UpdateExpression="set leaveByYear.#y.totalHoursUsed=:h",
                ExpressionAttributeNames={'#y': year},
                ExpressionAttributeValues={
                        ':h': hoursUsed
                        },
                ReturnValues="UPDATED_NEW"
                )
        return response
    except ClientError as e:
        print(e.response['Error']['Message'])

def insert_new_leave_year(eid, year, table):
    try:
        response = table.update_item(
                Key={'employeeId': eid},
                UpdateExpression="set leaveByYear.#y=:x",
                ExpressionAttributeNames={'#y': year},
                ExpressionAttributeValues={
                        ':x': {'totalHoursUsed': 0,
                               'requested': []
                               }
                        },
                ReturnValues="UPDATED_NEW"
                )
        return response
    except ClientError as e:
        print(e.response['Error']['Message'])

def insert_time_request(eid, year, eventData, table):
    try:
        response = table.update_item(
                Key={'employeeId': eid},
                UpdateExpression="set leaveByYear.#y.requested=list_append(leaveByYear.#y.requested, :e)",
                ExpressionAttributeNames={'#y': year},
                ExpressionAttributeValues={
                        ':e': [{
                                'start': eventData.start,
                                'end': eventData.end,
                                'accepted': eventData.accepted,
                                'hours': eventData.hours
                                }]
                        },
                ReturnValues="UPDATED_NEW"
                )
        return response
    except ClientError as e:
        print(e.response['Error']['Message'])