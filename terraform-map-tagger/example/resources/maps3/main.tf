#*********************
# Upload the 2 SAMPLE CSV files to the S3 bucket
resource "aws_s3_bucket_object" "migrationHubServerFileName" {
  bucket = var.bucketName
  key    = var.migrationHubServerFileName
  source = "../../samples/${var.migrationHubServerFileName}"
  etag = filemd5("../../samples/${var.migrationHubServerFileName}")
}
resource "aws_s3_bucket_object" "migrationHubAppFileName" {
  bucket = var.bucketName
  key    = var.migrationHubAppFileName
  source = "../../samples/${var.migrationHubAppFileName}"
  etag = filemd5("../../samples/${var.migrationHubAppFileName}")
}
#--------------------