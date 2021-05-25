# Readme
This directory is an example of how a customer may use the solution in the *src* directory, and it is dependent on that solution being installed first.

There are three example CloudFormation based solutions. One creates a simple EC2 instance, another creates an ASG using a LaunchTemplate that deploys an EC2 instance, and the final example demonstrates a more complete end to end VPC with ASG deployment. As part of provisioning, it will call the Tagging Automator Lambda function passing **appName** to return any relevant MAP 2.0 tags that should be applied to the AWS resources. 

## Prerequisite
1) Ensure the CUR-Automator solution is installed.  
2) Ensure the Server-IDs Automator solution is installed.  
3) Install the Tagging-Automator solution from the main **src** directory.  
4) Upload the **import-to-migrationhub.csv** in the **samples** directory to the S3 bucket created by the Originating-IDs solution. This creates a sample set of MAP tags for you to use.

More info on CUR-Automator and Originating-IDs solutions can be found here: https://s3-us-west-2.amazonaws.com/map-2.0-customer-documentation/tagging-instructions/MAP+Tagging+Instructions.pdf


## How to use examples
1. Create a new stack using the **cfn-webserver-env.yaml**, **cfn-dev-asg.yaml**, or **cfn-dev-ec2.yaml** file.  
2. Navigate to the console to see the new EC2 instances created with the appropriate MAP tags applied.   


## How to apply this to your CFN
Examine the sample CFN templates provided. 

In the Resources section, there is a resource with a logical name `LambdaGetMAPTags`. This resource invokes the Lambda function in order to get the appropriate MAP 2.0 tags. 

You can then set the resulting tag values to your AWS resources by calling `!GetAtt LambdaGetMAPTags.map-migrated` and/or `!GetAtt LambdaGetMAPTags.map-migrated-app`
