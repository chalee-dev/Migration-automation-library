# How to install the MAP 2.0 automation solution
The following steps are to be followed to install the solution.

## CUR Automator Solution
To install the CUR Automator Solution, there are a two manual RFCs that need to be submitted from the management account, and one manual configuration.

### Step 1: Deploy IAM resources for the CUR Automator  
Submit a *Create other* RFC requesting the IAM role be created. Use the following language for the RFC details:

#### RFC Information
**Account**: Management account  
**RFC Type**: Create other  
**Details**:  
Please create the following IAM role.  
{{paste in content of cur-automator-iam.yaml}}



### Step 2: Deploy the CUR Automator stack
Submit a *Create other* RFC requesting the stack to be created. After you submit the RFC, attach the cur-automator.yaml file as a comment. Use the following language for the RFC details.

#### RFC Information
**Account**: Management account  
**RFC Type**: Create other  
**Details**:  
Please create a stack from the attached cur-automator.yaml file.  

Parameters:
* S3Region - {{Specify the home region for MALZ}}

Stack Name:
* map-cur



### Step 3: Activate cost allocation tags
Federate into the Management account with the *AWSManagedServicesBillingRole*. Manually activate cost allocation tags according to the MAP tagging instructions.  


---

## Server IDs Automator
To install the Server IDs Automator Solution, there are a four RFCs that need to be submitted from a centralized application account. Determine which application account will be used to centrally utilize the Server IDs automator. This will be the account where all of the following RFCs will be filed.


### Step 1: Deploy IAM Resources for the Server IDs Automator  
Submit a *Create other* RFC requesting the IAM role be created. Use the following language for the RFC details:

#### RFC Information
**Account**: Centralized Application Account  
**RFC Type**: Create other  
**Details**:  
Please create the following IAM role.   
{{paste in content of originating-ids-automator-iam.yaml}}



### Step 2: Set the AWS Migration Hub home region
Submit a *Create other* RFC requesting the AWS Migration Hub home region to be set. Use the following language for the RFC details.  

#### RFC Information
**Account**: Centralized Application Account  
**RFC Type**: Create other  
**Details**:  
Set the AWS Migration Hub home region to {{Specify the home region for MALZ}}. This will be used by programmatic API access through Lambda only.   
Steps:  
* Navigate to AWS Migration Hub
* Set the region to {{Specify the home region for MALZ}}



### Step 3: Deploy the Server IDs Automator Stack
Submit a *Create Stack from CloudFormation (CFN) Template* RFC to deploy the Server IDs Automator.  

#### RFC Information
**Account**: Centralized Application Account   
**RFC Type**: Create Stack from CloudFormation (CFN) Template  
**Name**: map-server-ids-automator  
**CloudFormation template**: {{paste in content or originating-ids-automator.yaml}}  
**Parameters**:  
* MPE: {{Customer MPE ID (e.g: MPE012345)}}
* S3Region - {{Specify the home region for MALZ}}



### Step 4: Share the Server IDs Automator S3 bucket with the Organization  
Submit a *Create other* RFC requesting the following bucket policy be applied. Use the following language for the RFC details.

#### RFC Information
**Account**: Centralized Application Account   
**RFC Type**: Create other  
{{Adjust the policy below with the account ID and AWS Organization ID}}  
**Details**:  
Apply the following bucket policy to the migration-hub-inventory-bucket-{{Centralized App Account ID}} S3 bucket.  

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::migration-hub-inventory-bucket-{{Centralized App Account ID}}/OutputFiles/*",
                "arn:aws:s3:::migration-hub-inventory-bucket-{{Centralized App Account ID}}"
            ],
            "Condition": {
                "StringEquals": {
                    "aws:PrincipalOrgID": ["{{AWS Organization ID}}"]
                }
            }
        },
        {
            "Sid": "AllowSSLRequestsOnly",
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::migration-hub-inventory-bucket-{{Centralized App Account ID}}",
                "arn:aws:s3:::migration-hub-inventory-bucket-{{Centralized App Account ID}}/*"
            ],
            "Condition": {
                "Bool": {
                    "aws:SecureTransport": "false"
                }
            }
        }
    ]
}
```

---

## MAP Tagging Automator

### Step 1: Create a StackSet to deploy Tagging Automator to all app accounts
Submit a *Create other* RFC from the Management Account requesting that a new StackSet be created. Use the following language for the RFC details.

#### RFC Information
**Account**: Management account  
**RFC Type**: Create other  
**Details**:  
Configure the map-tagging-automator.yaml file as a stackset. The CFN is here: http://map-automation-us-east-1.s3.amazonaws.com/map-tagging-automator.yaml. {{Adjust the CFN region for the S3 region of your MALZ to pull the right file}.

This stackset must to be applied to all app accounts in the Applications OU ({{Applications OU Id}}).  

StackSet Name: map-tagging-automator

Parameters:
* LambdaSourceS3BucketName - map-tagging-automator-sourcecode-{{Centralized App Account ID}}
* MapAutomatorMigrationHubInOutS3BucketName - migration-hub-inventory-bucket-{{Centralized App Account ID}}

Tags:
* OUs: {{Applications OU Id}}

Deployment Targets:
* Deploy to Organization Units: {{Applications OU Id}}

Regions: {{Specify the home region for MALZ}}
