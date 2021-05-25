# Readme
This directory is an example of how a customer may use the solution in the *src* directory, and it is dependent on that solution being installed first.

This example Terraform solution creates a pair of EC2 instances for a mock dev environment. As part of provisioning, it will call the `getMapTagsForHost` Lambda function passing the **hostName** and **appName** to return any relevant MAP 2.0 tags that should be applied to the AWS resources. 

# Prerequisite
The solution in the main **src** directory must be installed so that the S3 bucket and Lambda function is created. See the readme in the **src** directory for more information.

# Components

**environments/dev/main.tf**  
Creates a pair of EC2 instances for a mock dev environment. It also uploads the latest set of CSV files downloaded from AWS Migration Hub, which are needed for the MAP lookup.

**environments/dev/variables.tf**  
A set of variables used for the mock dev environment. Update the `s3BucketName` and `migrationProjectId` accordingly.

**resources/ec2/main.tf**  
A resource template to create an EC2 instance. These are called from modules within the environments/dev/main.tf.

**resources/ec2/variables.tf**  
Variables required to provision the EC2 instance. These are populated from modules within the environments/dev/main.tf.

**resources/maplambda/main.tf**  
A resource template to invoke the MAP Lambda function. These are called from modules within the environments/dev/main.tf.

**resources/maplambda/output.tf**  
The result of the MAP Lambda function invocation are stored in the output variables. These are then used by modules within the environments/dev/main.tf.

**resources/maplambda/variables.tf**   
Variables required to invoke the MAP Lambda function. These are populated from modules within the environments/dev/main.tf.

**resources/maps3/main.tf**  
A resource template to upload the two AWS Migration Hub CSV files into S3. These are called from modules within the environments/dev/main.tf.

**resources/maps3/output.tf**  
The result of the S3 upload is stored in an output variable so that we can use it as a dependency for other resources.

**resources/maps3/variables.tf**   
Variables required to upload the CSV files to S3. These are populated from modules within the environments/dev/main.tf.

# Samples
The **samples** directory contains sample AWS Migraiton Hub files needed to execute the example. The Application.csv and Server.csv files were pulled down from AWS Migraiton Hub following the instructions for MAP by executing `aws discovery start-export-task` and `aws discovery describe-export-tasks` to obtain and download the resulting CSVs.

# Execute Example Solution
1. Follow the installation instructions in the main **src** folder to create the S3 bucket and upload the Lambda function.
2. Update the AWS Provider Profile and region with your account details in **environments/dev/main.tf**.
3. Update the S3 Bucket Name to match the new name you previously decided in **environments/dev/variables.tf**.
4. Navigate into the `environments/dev` folder and run `terraform init`.  
5. Run `terraform apply` to execute the changes for your environment.
6. Navigate to the console to see two new EC2 instances created with the appropriate MAP tags applied.

# Cleanup
Simply execute `terraform destroy` to remove the instances and CSV files.