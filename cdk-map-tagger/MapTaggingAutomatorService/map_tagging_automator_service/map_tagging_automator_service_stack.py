from aws_cdk import core as cdk

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core

from map_tools_service import map_tools_service

class MapTaggingAutomatorServiceStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        migrationHubBucketName = core.CfnParameter(self, "MapAutomatorMigrationHubInOutS3BucketName", 
            type="String", 
            description="The S3 bucket name where the MigrationHub files are located. This is the S3 bucket that you upload your inventory to.")

        service = map_tools_service.MapToolsService(self, 
                        "MapTaggingAutomator", 
                        props=migrationHubBucketName)
