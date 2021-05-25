provider "aws" {
  profile    = "map-terraform"
  region     = "us-west-2"
}

#*********************
# configuration for Lambda IAM Execution Role
data "aws_iam_policy" "AmazonS3ReadOnlyAccess" {
  arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}
data "aws_iam_policy" "AWSLambdaBasicExecutionRole" {
  arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
#--------------------

#*********************
# s3 bucket which will store the 3 files 
# (main tracking file, server file from migration hub, app file from migration hub)
resource "aws_s3_bucket" "S3Bucket" {
    bucket = "map-lookup-2020"
}
resource "aws_s3_bucket_public_access_block" "S3Bucket" {
  bucket = aws_s3_bucket.S3Bucket.id

  block_public_acls   = true
  block_public_policy = true
  ignore_public_acls  = true
  restrict_public_buckets = true
}
#--------------------

#*********************
# Create the lambda function that will perform the lookup and return the values for the MAP program tags
resource "aws_lambda_function" "getMapTagsForHost" {
    description = "Look up the MAP program tags for Server and App based on the hostname."
    function_name = "getMapTagsForHost"
    handler = "lambda_getMapTagsForHost.lambda_handler"
    filename = data.archive_file.lambda-code.output_path
    source_code_hash = data.archive_file.lambda-code.output_base64sha256

    memory_size = 128
    role = aws_iam_role.IAMRole.arn
    runtime = "python3.8"
    timeout = 3
    tracing_config {
        mode = "PassThrough"
    }
}
data "archive_file" "lambda-code" {
  type        = "zip"
  output_path = "lambda_getMapTagsForHost.zip"
  source {
    content  = file("lambda_getMapTagsForHost.py")
    filename = "lambda_getMapTagsForHost.py"
  }
}
#--------------------

#*********************
# IAM Role needed to execute the lambda function
resource "aws_iam_role" "IAMRole" {
    path = "/"
    name = "MapS3SelectLambdaRole"
    assume_role_policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"lambda.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
    max_session_duration = 3600
}

resource "aws_iam_role_policy_attachment" "s3readonly-role-policy-attach" {
  role       = aws_iam_role.IAMRole.name
  policy_arn = data.aws_iam_policy.AmazonS3ReadOnlyAccess.arn
}

resource "aws_iam_role_policy_attachment" "lambdaexecution-role-policy-attach" {
  role       = aws_iam_role.IAMRole.name
  policy_arn = data.aws_iam_policy.AWSLambdaBasicExecutionRole.arn
}