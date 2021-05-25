#Copyright 2008-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

#Permission is hereby granted, free of charge, to any person obtaining a copy of this
#software and associated documentation files (the "Software"), to deal in the Software
#without restriction, including without limitation the rights to use, copy, modify,
#merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
#permit persons to whom the Software is furnished to do so.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
#INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
#PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
#OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from __future__ import print_function
import boto3
import botocore
import json
import sys
import os
from botocore.exceptions import ClientError


HOST = 'https://console.cloudendure.com'
headers = {'Content-Type': 'application/json'}
session = {}
endpoint = '/api/latest/{}'

application = os.environ['application']
environment = os.environ['environment']
servers_table_name = '{}-{}-servers'.format(application, environment)
apps_table_name = '{}-{}-apps'.format(application, environment)
servers_table = boto3.resource('dynamodb').Table(servers_table_name)
apps_table = boto3.resource('dynamodb').Table(apps_table_name)

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


def lambda_handler(event, context):
    print(event)
    dbresponse = servers_table.scan()
    projectname = str(event["Event"]["projectname"])
    print(projectname)
    rfc_ids = str(event["Event"]["rfc_id_info"])
    rfc_list = rfc_ids.split(',')
    rfc_list = filter(None, rfc_list)
    server_ids = str(event["Event"]["server_id"])
    server_id_list = server_ids.split(',')
    server_id_list = filter(None, server_id_list)
    SecretValue = GetSecretData(projectname)
    access_key_id = SecretValue["SecretString"].split(';')[0].split(':')[
        1].strip()
    secret_access_key = SecretValue["SecretString"].split(';')[1].split(':')[
        1].strip()
    rfc_id_info = ""
    server_id_info = ""
    TaskStatus = ""
    for i in range(len(rfc_list)):
        rfc_id = rfc_list[i]
        server_id = server_id_list[i]
        ams_client = boto3.client(
            'amscm', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)
        rfc_details = ams_client.get_rfc(RfcId=rfc_id)
        rfc_status = str(rfc_details['Rfc']['Status']['Id'])
        print(rfc_status)
        if rfc_status.lower() == "wig rfc in progress" or rfc_status.lower() == "inprogress" or rfc_status.lower() == "pendingapproval" or rfc_status.lower() == "in progress":
                rfc_id_info = rfc_id_info + rfc_id + ","
                server_id_info = server_id_info + server_id + ","
        else:
            try:
                for j in dbresponse['Items']:
                    json_str = json.dumps(j, cls=DecimalEncoder)
                    resp_dict = json.loads(json_str)
                    if j['server_id'] == server_id:
                        resp_dict.update({"rfc_status": rfc_status})
                        servers_table.put_item(
                            Item=resp_dict
                        )
            except ClientError as e:
                print(e.dbresponse['Error']['Message'])

    if rfc_id_info == "" or rfc_id_info == ",":
        TaskStatus = "Complete"
        Input = {"projectname": projectname, "rfc_id_info": rfc_id_info,
                 "server_id": server_id_info, "TaskStatus": TaskStatus}
        return Input
    else:
        TaskStatus = "In Progress"
        Input = {"projectname": projectname, "rfc_id_info": rfc_id_info,
                 "server_id": server_id_info, "TaskStatus": TaskStatus}
        return Input


def GetSecretData(projectname):
    secret_client = boto3.client('secretsmanager')
    try:
        response = secret_client.get_secret_value(
            SecretId='MF_Secret_' + projectname
        )
        return response
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print("The requested secret was not found")
