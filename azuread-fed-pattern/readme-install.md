## Installation Overview

Steps:
1) From the Management account, execute cfn-azuread-fed-admin-role.yaml in CloudFormation
Parameters required:
  OrganizationId: 
  SAMLProviderName: 

2) From the root Management account, create a StackSet in CloudFormation using cfn-azuread-fed-stackset.yaml. Apply it to all accounts in the Organization (or specific OUs if appropriate). Add a tag to show which OU IDs were deployed.
Parameters required:
  ManagementAccountId: 

3) Customer needs to security obtain the IAM access keys stored in Secrets Manager in the Management account and then configure the IAM Role sync from within Azure (Ref: https://docs.microsoft.com/en-us/azure/active-directory/saas-apps/amazon-web-service-tutorial)

4) Customer uses the workflow described in the readme.md to obtain the IAM user access keys for all other member accounts and configures Azure AD accordingly.

