#########################################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.                    #
# SPDX-License-Identifier: MIT-0                                                        #
#                                                                                       #
# Permission is hereby granted, free of charge, to any person obtaining a copy of this  #
# software and associated documentation files (the "Software"), to deal in the Software #
# without restriction, including without limitation the rights to use, copy, modify,    #
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to    #
# permit persons to whom the Software is furnished to do so.                            #
#                                                                                       #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,   #
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A         #
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT    #
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION     #
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE        #
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                                #
#########################################################################################

import json
import boto3
import logging
import os
import datetime
import time

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
        "b"."server_os_version" , \
        "b"."replication_status" , \
        "b"."server_environment" \
        FROM "migration-tracker-server-extract-table" b \
        LEFT JOIN "migration-tracker-app-extract-table" a \
        ON "b"."app_id" = "a"."app_id"'


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
