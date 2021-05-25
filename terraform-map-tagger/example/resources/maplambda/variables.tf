variable "bucketName" {}
variable "hostName" {}
variable "appName" {}
variable "migrationHubServerFileName" {}
variable "migrationHubAppFileName" {}

# dummy variable for dependency tracking to ensure S3 files are loaded before lambda runs
variable "target_group_depends_on" {
  type    = any # only the dependencies matter, not the value
  default = null
}
