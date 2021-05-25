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

from sqlescapy import sqlescape

import json
import boto3

def getMapTags(mapMigrationHubS3BucketName, appName, awsRegion):
    originatingServerId=""
    originatingAppId=""

    # santize S3 Select input
    appName = sqlescape(appName.strip())

    print('bucketName: ' + mapMigrationHubS3BucketName)
    print('appName: ' + appName)
    print('region: ' + awsRegion)
    
    fileNames = getS3FileKeys(mapMigrationHubS3BucketName)
    
    if not fileNames['server_key']:
        raise ValueError("Migration hub files were not found in " + mapMigrationHubS3BucketName)
    
    migrationHubServerFileName = fileNames['server_key']
    migrationHubAppFileName = fileNames['app_key']
    
    # Get the OriginatingAppId from the MigrationHub App CSV
    s3 = boto3.client('s3', region_name=awsRegion)
    s3Response = s3.select_object_content(
            Bucket=mapMigrationHubS3BucketName,
            Key=migrationHubAppFileName,
            ExpressionType='SQL',
            Expression=f"""SELECT s.Id 
                            FROM s3object s 
                            WHERE 
                                s.name = '{appName}'
                            LIMIT 1""",
            InputSerialization={'CSV':{'FileHeaderInfo':'Use'},'CompressionType':'NONE'},
            OutputSerialization={'CSV':{}}
        )
    for event in s3Response['Payload']:
        if 'Records' in event:
            originatingAppId = event['Records']['Payload'].decode('utf-8').strip()

    if originatingAppId != '':
        # santize S3 Select input
        originatingAppId = sqlescape(originatingAppId)

        # Get the OriginatingServerId from the MigrationHub Server CSV
        s3Response = s3.select_object_content(
                Bucket=mapMigrationHubS3BucketName,
                Key=migrationHubServerFileName,
                ExpressionType='SQL',
                Expression=f"""SELECT s.configId 
                                FROM s3object s 
                                WHERE 
                                    s.applicationConfigurationId = '{originatingAppId}'
                                LIMIT 1""",
                InputSerialization={'CSV':{'FileHeaderInfo':'Use'},'CompressionType':'NONE'},
                OutputSerialization={'CSV':{}}
            )
        for event in s3Response['Payload']:
            if 'Records' in event:
                originatingServerId = event['Records']['Payload'].decode('utf-8').strip()
    
    print('map-migrated: {}, map-migrated-app: {}'.format(originatingServerId, originatingAppId))
    
    output = {}
    output['map-migrated'] = originatingServerId
    output['map-migrated-app'] = originatingAppId

    return output

# Helper function to find the most recent server an application csv files from MigrationHub
def getS3FileKeys(s3BucketName):
    s3 = boto3.session.Session().resource('s3')
    bucket = s3.Bucket(s3BucketName)
    folders = bucket.objects.filter(Prefix='OutputFiles/import ', Delimiter='')

    files = [obj for obj in sorted(folders, key=lambda x: x.key, reverse=True)]
    
    # Find the first server and application csv from the sorted list
    serverFileKey = ''
    appFileKey = ''
    for file in files:
        if file.key.endswith('_ApplicationResourceAssociation.csv'):
            print('##Found ApplicationResourceAssociation: ' + file.key)
            serverFileKey = file.key
        if file.key.endswith('_Application.csv'):
            print('##Found Application: ' + file.key)
            appFileKey = file.key
        if (serverFileKey != '' and appFileKey != ''):
            break
    
    output = {}
    output['server_key'] = serverFileKey
    output['app_key'] = appFileKey
    
    return output