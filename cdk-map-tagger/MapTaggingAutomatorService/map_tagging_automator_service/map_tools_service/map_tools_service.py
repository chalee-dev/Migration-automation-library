from aws_cdk import (core,
                     aws_lambda as lambda_,
                     aws_iam as iam)

class MapToolsService(core.Construct):
    def __init__(self, scope: core.Construct, id: str, props: core.StackProps):
        super().__init__(scope, id)

        # Create policies for the Lambda
        lambdaS3Policy = iam.Policy(self, "MapAutomatorMigrationHubInOutS3BucketAccess", 
            policy_name="MapAutomatorMigrationHubInOutS3BucketAccess")
        lambdaS3Policy.document.add_statements(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            resources=[
                f'arn:aws:s3:::{props.value_as_string}/*',
                f'arn:aws:s3:::{props.value_as_string}',
            ],
            actions=[
                "s3:GetObject",
                "s3:ListBucket"
            ]
        ))
        lambdaPolicy = iam.Policy(self, "LambdaExecutionRoleForLogGroup", 
            policy_name="LambdaExecutionRoleForLogGroup")
        lambdaPolicy.document.add_statements(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            resources=[
                f'arn:aws:logs:{core.Aws.REGION}:{core.Aws.ACCOUNT_ID}:log-group:/aws/lambda/mapAutomator-GetMapTagsForHost-{core.Aws.ACCOUNT_ID}:*'
            ],
            actions=[
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ]
        ))

        # Create a custom role with the custom policies for the Lambda
        lambdaRole = iam.Role(self, "LambdaIAMRole",
            role_name=f'mapAutomator-S3SelectLambdaRole-{core.Aws.ACCOUNT_ID}',
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )
        lambdaRole.attach_inline_policy(lambdaS3Policy)
        lambdaRole.attach_inline_policy(lambdaPolicy)

        # Create the lambda layer and the function
        layer = lambda_.LayerVersion(self, "MAPToolsLambdaLayer",
                    layer_version_name="mapTools",
                    description="MAP 2.0 tools library",
                    compatible_runtimes=[lambda_.Runtime.PYTHON_3_7],
                    code=lambda_.Code.from_asset("resources/mapTools"))

        handler = lambda_.Function(self, "MAPTagLookupLambda",
                    function_name=f'mapAutomator-GetMapTagsForHost-{core.Aws.ACCOUNT_ID}',
                    description="Look up the MAP program tags for Server and App based on the app name",
                    runtime=lambda_.Runtime.PYTHON_3_7,
                    code=lambda_.Code.from_asset("resources/getMapTags"),
                    handler="getMapTags.handler",
                    role=lambdaRole,
                    layers=[layer],
                    timeout=core.Duration.seconds(5),
                    environment=dict(
                        MAP_MIGRATION_HUB_S3_BUCKET_NAME=props.value_as_string)
                    )

        core.CfnOutput(self, export_name="MAPMigration-TagLookupLambdaArn",
                        id="MAPTagLookupLambdaArn",
                        value=handler.function_arn,
                        description="The ARN for the Lambda used to look up the MAP program tags for Server and App based on the hostname")