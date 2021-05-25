import json
import boto3

s3 = boto3.client('s3', region_name='us-west-2')

def lambda_handler(event, context):
    bucketName = event['bucketName']
    hostName = event['hostName']
    appName = event['appName']
    migrationHubServerFileName = event['migrationHubServerFileName']
    migrationHubAppFileName = event['migrationHubAppFileName']
    
    # Get the OriginatingServerId from the MigrationHub Server CSV
    s3Response = s3.select_object_content(
            Bucket=bucketName,
            Key=migrationHubServerFileName,
            ExpressionType='SQL',
            Expression=f"""SELECT s.Id 
                            FROM s3object s 
                            WHERE 
                                s.hostName = '{hostName}'
                            LIMIT 1""",
            InputSerialization={'CSV':{'FileHeaderInfo':'Use'},'CompressionType':'NONE'},
            OutputSerialization={'CSV':{}}
        )
    originatingServerId=""
    for event in s3Response['Payload']:
        if 'Records' in event:
            originatingServerId = event['Records']['Payload'].decode('utf-8').strip()
        
    # Get the OriginatingAppId from the MigrationHub App CSV
    s3Response = s3.select_object_content(
            Bucket=bucketName,
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
    originatingAppId=""
    for event in s3Response['Payload']:
        if 'Records' in event:
            originatingAppId = event['Records']['Payload'].decode('utf-8').strip()
    
    return {
        'statusCode': 200,
        "isBase64Encoded": 'false',
        'body': json.dumps({ "aws-migrated": originatingServerId, "aws-migrated-app": originatingAppId})
    }
