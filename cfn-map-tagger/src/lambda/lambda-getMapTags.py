# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from crhelper import CfnResource

import json
import boto3
import os
import mapTools

helper = CfnResource(log_level='DEBUG')

def handler(event, context):
    print(event)
    helper(event, context)
    
@helper.create
@helper.update
def getTags(event, context):
    print('### Event: ')
    print(event)
    
    bucketName = os.environ['MAP_MIGRATION_HUB_S3_BUCKET_NAME']
    appName = event['ResourceProperties']['appName']
    region = os.environ['AWS_REGION']

    print('bucketName: ' + bucketName)
    print('appName: ' + appName)
    print('region: ' + region)

    results = mapTools.getMapTags(bucketName, appName, region)

    print('map-migrated: {}, map-migrated-app: {}'.format(results['map-migrated'], results['map-migrated-app']))
    
    helper.Data.update({"map-migrated": results['map-migrated']})
    helper.Data.update({"map-migrated-app": results['map-migrated-app']})
