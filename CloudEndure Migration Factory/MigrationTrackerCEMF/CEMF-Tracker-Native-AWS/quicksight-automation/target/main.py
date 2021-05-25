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


def custom_resource_handler(event, context):
	print("Event JSON: \n" + dumps(event))

	dashboard_name = event['ResourceProperties']['NewDashboardName']
	template_name = event['ResourceProperties']['SourceTemplateName']
	source_acct_no = event['ResourceProperties']['SourceAcctNo']
	username = event['ResourceProperties']['UserName']

	region = os.environ['AWS_REGION']

	src_template_arn = 'arn:aws:quicksight:' + region + ':' + source_acct_no + ':template/' + template_name
	print(src_template_arn)

	quicksight = boto3.client('quicksight')
	sts = boto3.client('sts')

	account_number = sts.get_caller_identity()['Account']

	if event['RequestType'] == 'Create':
		try:
			dataset_arn = get_dataset(quicksight, account_number)
			create_analysis(quicksight, account_number, src_template_arn, username, dashboard_name)
			dashboard = quicksight.create_dashboard(
				AwsAccountId = account_number,
				DashboardId = dashboard_name,
				Name = dashboard_name,
				SourceEntity = {
					'SourceTemplate': {
						'Arn': src_template_arn,
						'DataSetReferences': [
							{
								'DataSetPlaceholder': 'app_id,app_name,cloudendure_projectname,instancetype,IntMigrationStatusSummary,migration_status,MigrationStatusSummary,replication_status,server_environment,server_fqdn,server_id,server_name,server_os,wave_id',
								'DataSetArn' : dataset_arn
							}
						]
					}
				},
				Permissions = [{
					'Principal': 'arn:aws:quicksight:' + region + ':' + account_number + ':user/default/' + username,
					'Actions': ['quicksight:DescribeDashboard', 'quicksight:ListDashboardVersions', 'quicksight:UpdateDashboardPermissions', 'quicksight:QueryDashboard', 'quicksight:UpdateDashboard', 'quicksight:DeleteDashboard', 'quicksight:DescribeDashboardPermissions', 'quicksight:UpdateDashboardPublishedVersion']
				}]
			)

			response = 'SUCCESS'

		except quicksight.exceptions.ResourceExistsException:
			print(f'The resource already exists.')
			log_exception()
			response = 'SUCCESS'

		except Exception as e:
			print(f'An error has occured in the function create_template {e}.')
			log_exception()
			response = 'FAILED'

		send_response(event, context, response)
		return

	if event['RequestType'] == 'Update':
		# Do nothing and send a success immediately
		send_response(event, context, response)
		return

	if event['RequestType'] == 'Delete':
		delete_analysis(quicksight, account_number, dashboard_name)
		try:
			response = quicksight.delete_dashboard(
				AwsAccountId = account_number,
				DashboardId = dashboard_name
			)

			response = 'SUCCESS'

		except quicksight.exceptions.ResourceNotFoundException:
			print(f'The resource does not exist. No need to delete')
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

def create_analysis(quicksight, account_number, src_template_arn, username, dashboard_name):
	try:
		ds_name = dashboard_name
		template_arn = src_template_arn
		owner_name = username
		dataset_arn = get_dataset(quicksight, account_number)
		response = quicksight.create_analysis(
			AwsAccountId = account_number,
			AnalysisId = ds_name,
			Name = ds_name,
			SourceEntity = {
				'SourceTemplate': {
					'Arn': template_arn,
					'DataSetReferences': [
						{
							'DataSetPlaceholder': 'app_id,app_name,cloudendure_projectname,instancetype,IntMigrationStatusSummary,migration_status,MigrationStatusSummary,replication_status,server_environment,server_fqdn,server_id,server_name,server_os,wave_id',
							'DataSetArn' : dataset_arn
						}
					]
				}
			},
			Permissions = [{
				'Principal': 'arn:aws:quicksight:us-east-1:' + account_number + ':user/default/' + owner_name,
				'Actions': ['quicksight:RestoreAnalysis', 'quicksight:UpdateAnalysisPermissions', 'quicksight:DeleteAnalysis', 'quicksight:QueryAnalysis', 'quicksight:DescribeAnalysisPermissions', 'quicksight:DescribeAnalysis', 'quicksight:UpdateAnalysis']
			}]
	)


	except quicksight.exceptions.ResourceExistsException:
		print(f'The resource already exists.')
		log_exception()
		pass

	except Exception as e:
		log_exception()
		raise

def delete_analysis(quicksight, account_number, dashboard_name):
	analysis_id = dashboard_name
	try:
		response = quicksight.delete_analysis(
			AwsAccountId = account_number,
			AnalysisId = analysis_id
		)

	except quicksight.exceptions.ResourceNotFoundException:
		print(f'The resource does not exist. No need to delete')
		log_exception()

	except Exception as e:
		log_exception()
		raise

def lambda_handler(event, context):
	try:
		return custom_resource_handler(event, context)

	except Exception as e:
		log_exception()
		raise