variable "migrationProjectId" {
    default = "MPE123456"  # Replace with customer's MAP project Id
}

variable "s3BucketName" {
    default = "map-lookup-2020"
}
variable "migrationHubServerFileName" {
    default = "Server.csv"
}
variable "migrationHubAppFileName" {
    default = "Application.csv"
}

variable "lambda_getMapTagsForHost" {
    default = []
}