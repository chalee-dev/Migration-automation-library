# Readme
This directory contains the CFN template that will create the infrastructure needed to perform the MAP 2.0 tag lookup automation. This solution enables customers that are migrating using Rehost and Refactor patterns to automate the process of applying MAP 2.0 tags to their resources as they are being deployed. It leverages a Lambda function which takes in the application name being migrated and returns originating server id and originating application id. The caller can then apply the tags to the resource accordingly.

See the *example* directory for an example of how a customer may use this solution once it is installed.


## Installation
Run the `map-tagging-automator.yaml` in CloudFormation. Be sure to run it in the same region as the originating-ids-automator solution.

## Post-Install Examples
See the *example* directory on how to invoke the Lambda to get the MAP 2.0 tag values for your CloudFormation templates. The directory contains two examples.

## Cleanup
1. Delete the CFN stack. ;)

## Components

### cfn-map-tagging-automator.yaml
This is the CFN that needs to be executed to create the resources that will determine MAP tags for a given application name. 

| Name | Type | Description |
| ---- | ---- | ----------- |
| LambdaIAMRole | IAM Role | Used by Lambda to execute an S3 Select.  Least priviledge policies allowing Lambda to read the MigrationHub-In-Out files created by the Originating-IDs Automator (reference: https://map-automation.s3-us-west-2.amazonaws.com/MAP-Tagging-Automator-Instructions.pdf) |
| MAPTagLookupLambda | Lambda Function | Python based Lambda function that determines the MAP 2.0 tags for a given application name. |
| MAPMigration-TagLookupLambdaArn | CFN Export | This is the Lambda ARN that will perform the tag lookup. Customers will need to use this in order to invoke the function in their CFN to get the MAP tags |


## FAQ
**Q: What types of MAP 2.0 tags does this solution currently support?**  
A: The Originating IDs Automator can generate all of the MAP 2.0 tags. The Tagging Automator solution currently only maps map-migrated and map-migrated-app tags.

**Q: Can this solution be used in a multi-account solution?**  
A: Yes. Prescriptive guidance on setting this up for multi-account customers can be found {{insert link}}  

**Q: Do you have examples of how to use the solution?**  
A: Yes. See the *example* directory.  

**Q: What regions does this support?**  
A: Currently this solution only supports regions that are supported by AWS Migration Hub.

**Q: What fields are required in the server inventory.xlsx file for AWS Migration Hub?**
A: In addition to one of the required primary key fields, this solution requires the use of the `Applications` column. The name provided in the `Applications` column must be passed into the Tagging Automator to perform the lookup. 
