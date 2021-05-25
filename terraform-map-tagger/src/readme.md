# Readme
This directory contains the Terraform files that will create the infrastructure needed to perform the MAP 2.0 tag lookup. See the *example* directory for an example of how a customer may use this solution once it is installed.


# Components

| Name | Type | Description |
| ---- | ---- | ----------- |
| MapS3SelectLambdaRole | IAM Role | Used by Lambda to execute an S3 Select.  Policies: AmazonS3ReadOnlyAccess, AWSLambdaBasicExecutionRole |
| getMapTagsForHost | Lambda Function | Python based Lambda function that determines the MAP 2.0 tags for a given host name. Currently configured to use s3 in us-west-2. |
| map-lookup-2020 | S3 Bucket | Your bucket that will host the 2 AWS Migration Hub CSV files needed by the Lambda function. Customize bucket name accordingly. |



# Installation
Apply this terraform code to an AWS account that will be used to keep track of the MAP 2.0 credits.

1. Update the AWS Provider Profile and region with your account details in **main.tf**.
3. Update the S3 Bucket Name in **main.tf** from *map-lookup-2020* to be a new name that is not in use.
4. Ensure the lambda_getMapTagsForHost.py function is using the same region for s3 as configured in step 1.  
5. Run `terraform init`.
6. Run `terraform apply` to install the solution components for your environment.

# Cleanup
Simply execute `terraform destroy` to remove the resources from the account.