import json
import boto3
import logging
import os
import datetime
import time
import requests
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()
log.setLevel(logging.DEBUG)

application = os.environ['application']
environment = os.environ['environment']
database = "migration-tracker"
query = 'CREATE \
        OR REPLACE VIEW migration_tracker_general_view AS \
        SELECT "a"."cloudendure_projectname" , \
        "a"."app_name" , \
        "a"."wave_id" ,\
        "a"."app_id", \
        "b"."server_name" , \
        "b"."instancetype" , \
        "b"."migration_status" , \
        "b"."server_id" , \
        "b"."server_fqdn" , \
        "b"."server_os" , \
        "b"."replication_status" , \
        "b"."server_environment" \
        FROM "migration-tracker-app-extract-table" a \
        LEFT JOIN "migration-tracker-server-extract-table" b \
        ON "a"."app_id" = "b"."app_id"'


def lambda_handler(event, context):
    log.info('Function Starting')
    log.info(f'Incoming Event:\n{json.dumps(event,indent=2)}')
    log.info(f'Context Object:\n{vars(context)}')
    aws_account_id = context.invoked_function_arn.split(":")[4]
    athena_result_bucket = "s3://{}-{}-{}-athena-results/".format(
        application, environment, aws_account_id)
    athena_client = boto3.client("athena")
    response = athena_client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={'Database': database,
                               'Catalog': 'AwsDataCatalog'},
        ResultConfiguration={
            'OutputLocation': athena_result_bucket,
        },
        WorkGroup='MigrationTrackerWorkGroup'
    )
