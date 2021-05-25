import boto3
import json
from datetime import date, datetime
import os
import logging
import traceback
import urllib.request
import time
import sys
from json import dumps

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def log_exception():
    "Log a stack trace"
    exc_type, exc_value, exc_traceback = sys.exc_info()
    print(repr(traceback.format_exception(
        exc_type,
        exc_value,
        exc_traceback)))

def send_response(event, context, response):
    "Send a response to CloudFormation to handle the custom resource lifecycle"

    responseBody = { 
        'Status': response,
        'Reason': 'See details in CloudWatch Log Stream: ' + \
            context.log_stream_name,
        'PhysicalResourceId': context.log_stream_name,
        'StackId': event['StackId'],
        'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId'],
    }

    print('RESPONSE BODY: \n' + dumps(responseBody))

    data = dumps(responseBody).encode('utf-8')
    
    req = urllib.request.Request(
        event['ResponseURL'], 
        data,
        headers={'Content-Length': len(data), 'Content-Type': ''})
    req.get_method = lambda: 'PUT'

    try:
        with urllib.request.urlopen(req) as response:
            print(f'response.status: {response.status}, ' + 
                  f'response.reason: {response.reason}')
            print('response from cfn: ' + response.read().decode('utf-8'))
    except urllib.error.URLError:
        log_exception()
        raise Exception('Received non-200 response while sending ' +\
            'response to AWS CloudFormation')

    return True

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)

def custom_resource_handler(event, context):
	print("Event JSON: \n" + dumps(event))

	dashboard_name = event['ResourceProperties']['DashboardName']
	template_name = event['ResourceProperties']['TemplateName']
	target_acct_no = event['ResourceProperties']['TargetAcctNo']

	quicksight = boto3.client('quicksight')
	sts = boto3.client('sts')

	account_number = sts.get_caller_identity()['Account']
	target_account_id = target_acct_no

	if event['RequestType'] == 'Create':
		try:
			template_id = create_template(quicksight, account_number, template_name, dashboard_name)
			quicksight.update_template_permissions(
				AwsAccountId = account_number,
				TemplateId = template_id,
				GrantPermissions = [
					{
						'Principal': 'arn:aws:iam::' + target_account_id + ':root',
						'Actions': ['quicksight:UpdateTemplatePermissions', 'quicksight:DescribeTemplate']
					}
				]
			)

			response = 'SUCCESS'

		except quicksight.exceptions.ResourceExistsException:
			print(f'The resource already exists.')
			log_exception()
			response = 'SUCCESS'

		except quicksight.exceptions.AccessDeniedException:
			print(f'You might not be authorized to carry out the request. Ensure that your account is authorized to use the Amazon QuickSight service, that your policies have the correct permissions, and that you are using the correct access keys.')
			log_exception()
			response = 'FAILED'

		except Exception as e:
			print(f'There was an error {e} creating a template.')
			log_exception()
			response = 'FAILED'
		
		send_response(event, context, response)
		return

	if event['RequestType'] == 'Update':
		# Do nothing and send a success immediately
		send_response(event, context, response)
		return

	if event['RequestType'] == 'Delete':
		try:
			quicksight.delete_template(
				AwsAccountId = account_number,
				TemplateId = template_name)
			
			response = 'SUCCESS'
		
		except quicksight.exceptions.ResourceNotFoundException:
			print(f'The template does not exist. {e}')
			log_exception()
			response = 'SUCCESS'
		
		except Exception as e:
			print(f'An error has occured in deleting the template {e}.')
			log_exception()
			response = 'FAILED'

		send_response(event, context, response)

def get_dataset(quicksight, account_number):
	try:
		response = quicksight.list_data_sets(
			AwsAccountId = account_number)

		dataset_arn = response['DataSetSummaries'][0]['Arn']
		return dataset_arn

	except Exception as e:
		print(f'An error has occured in the function get_dataset {e}.')
		log_exception()

def get_dashboard_arn(quicksight, account_number, dashboard_name):
	try:
		dashboards = quicksight.list_dashboards(
			AwsAccountId=account_number)

		dash_load = json.dumps(dashboards, cls=DateTimeEncoder)
		dash = json.loads(dash_load)

		for value in dash['DashboardSummaryList']:
			if value['Name'] == dashboard_name:
				dashboard_id = value['DashboardId']
				return dashboard_id

	except Exception as e:
		print(f'An error has occured in the function get_dashboard_arn {e}.')
		log_exception()

def get_dashboard_source_entity(quicksight, account_number, dashboard_name):
	try:
		dashboard_id = get_dashboard_arn(quicksight, account_number, dashboard_name)
		dashboards_result = quicksight.describe_dashboard(
			AwsAccountId = account_number,
			DashboardId = dashboard_id
		)

		source_entity = dashboards_result['Dashboard']['Version']['SourceEntityArn']

		return source_entity

	except Exception as e:
		print(f'An error has occured in the function get_dashboard_source_entity {e}.')
		log_exception()

def get_dashboard_datasource_arn(quicksight, account_number, dashboard_name):
	try:
		dashboard_id = get_dashboard_arn(quicksight, account_number, dashboard_name)
		dashboards_result = quicksight.describe_dashboard(
			AwsAccountId = account_number,
			DashboardId = dashboard_id
		)

		datasource_entity = dashboards_result['Dashboard']['Version']['DataSetArns']

		return datasource_entity
	
	except Exception as e:
		print(f'An error has occured in the function get_dashboard_datasource_arn {e}.')
		log_exception()

def create_template(quicksight, account_number, template_name, dashboard_name):
	template_id = template_name
	source_arn = get_dashboard_source_entity(quicksight, account_number, dashboard_name)
	source_dataset_entity = get_dashboard_datasource_arn(quicksight, account_number, dashboard_name)
	
	try:
		quicksight.create_template(
		AwsAccountId = account_number,
		TemplateId = template_id,
		Name = template_id,
		SourceEntity = {
			'SourceAnalysis': {
				'Arn': source_arn,
				'DataSetReferences': [
					{
						'DataSetPlaceholder': 'app_id,app_name,cloudendure_projectname,instancetype,IntMigrationStatusSummary,migration_status,MigrationStatusSummary,replication_status,server_environment,server_fqdn,server_id,server_name,server_os,wave_id',
						'DataSetArn': source_dataset_entity[0]
					}
				]
			}
		}
	)
		return template_id

	except quicksight.exceptions.ResourceExistsException:
		print(f'The resource already exists.')
		log_exception()
		return template_id
		
	except Exception as e:
		print(f'An error has occured in the function create_template {e}.')
		log_exception()

def lambda_handler(event, context):
	try:
		return custom_resource_handler(event, context)

	except Exception as e:
		log_exception()
		raise