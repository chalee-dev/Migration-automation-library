import json
import boto3
import logging
import os
import datetime
import time
from botocore.vendored import requests
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()
log.setLevel(logging.DEBUG)

application = os.environ['application']
environment = os.environ['environment']
glue_app_crawler_name= 'migration-tracker-app-crawler-{}'.format(environment)
glue_server_crawler_name= 'migration-tracker-server-crawler-{}'.format(environment)
glue_app_job_name="Migration_Tracker_App_Extract"
glue_server_job_name="Migration_Tracker_Server_Extract"

def lambda_handler(event, context):
    
    """Process a CloudFormation custom resource request.

    Returns: HTTP PUT request to s3-presigned URL
    """
    log.info('Function Starting')
    log.info(f'Incoming Event:\n{json.dumps(event,indent=2)}')
    log.info(f'Context Object:\n{vars(context)}')
    try:
        if (event['RequestType'] == 'Create') or (event['RequestType'] == 'Update'):
            response_data = run_glue_crawler_job()
            response_reason = 'Running the glue crawler and job'
            response_status = 'SUCCESS'

        elif event['RequestType'] == 'Delete':
            response_status = 'SUCCESS'
            response_reason = 'No cleanup is required for this function'
            response_data = None

        send_response(event, context, response_status, response_reason, response_data)

    except Exception as E:
        response_reason = f'Exception: {str(E)}'
        log.exception(response_reason)
        if event.get('PhysicalResourceId'):
            resource_id = event.get('PhysicalResourceId')
        else:
            resource_id = event.get('LogicalResourceId')

        send_response(event, context, 'FAILED', response_reason, resource_id)
    return ''
    
def run_glue_crawler_job():
    """Run the glue crawler and the glue."""
    
    glue_client = boto3.client('glue')
    response = glue_client.start_crawler(
        Name= glue_app_crawler_name
        )
    response = glue_client.start_crawler(
        Name= glue_server_crawler_name
        )
    time.sleep(30)
    response = glue_client.start_job_run(
        JobName= glue_app_job_name
        )
    response = glue_client.start_job_run(
        JobName= glue_server_job_name
        )
        

    return response


def send_response(event, context, response_status, response_reason, response_data):
    """Send response to CloudFormation via S3 presigned URL."""
    log.info('Sending response to CloudFormation')
    response_url = event['ResponseURL']
    log.info(f'Response URL: {response_url}')

    responseBody = {}

    responseBody['Status'] = response_status
    responseBody['PhysicalResourceId'] = context.aws_request_id
    responseBody['Reason'] = response_reason
    responseBody['StackId'] = event['StackId']
    responseBody['RequestId'] = event['RequestId']
    responseBody['LogicalResourceId'] = event['LogicalResourceId']
    if response_data:
        responseBody['Data'] = response_data

    json_responseBody = json.dumps(responseBody)

    log.info("Response body:\n" + json_responseBody)

    headers = {
        'content-type': '',
        'content-length': str(len(json_responseBody))
    }

    try:
        response = requests.put(response_url,
                                data=json_responseBody,
                                headers=headers,
                                timeout=5)
        log.info(f'HTTP PUT Response status code: {response.reason}')
    except Exception as E:
        log.error(f'CloudFormation Response API call failed:\n{E}')
