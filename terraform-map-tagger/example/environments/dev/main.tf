provider "aws" {
  profile    = "map-terraform"
  region     = "us-west-2"
}

#*********************
# copy the latest and greatest MAP files fetched from MigrationHub to S3
module "maps3_initialize" {
    source = "../../resources/maps3"
    bucketName = var.s3BucketName
    migrationHubServerFileName= var.migrationHubServerFileName
    migrationHubAppFileName= var.migrationHubAppFileName
}
#--------------------

#*********************
# create webserver
module "dev_webserver_maplambda" {
    source  = "../../resources/maplambda"
    hostName ="WA2AASW850D1"
    appName = "App2"
    migrationHubServerFileName= var.migrationHubServerFileName
    migrationHubAppFileName= var.migrationHubAppFileName
    bucketName = var.s3BucketName

    # Wait for resources and associations to be created
    target_group_depends_on = module.maps3_initialize.s3_id
}

module "dev_webserver" {
    source = "../../resources/ec2"
    ami = "ami-0a243dbef00e96192"
    instanceType = "t2.micro"
    subnetId = "subnet-0444f510ec8f7d2a8"
    name = "webserver"
    appMigrationedId = module.dev_webserver_maplambda.mapServerId
    serverMigratedId = module.dev_webserver_maplambda.mapAppId
    migrationProjectId = var.migrationProjectId
}
#--------------------

#*********************
# create appserver
module "dev_appserver_maplambda" {
    source  = "../../resources/maplambda"
    hostName ="DA2AAWS231D1"
    appName = "App3"
    migrationHubServerFileName= var.migrationHubServerFileName
    migrationHubAppFileName= var.migrationHubAppFileName
    bucketName = var.s3BucketName

    # Wait for resources and associations to be created
    target_group_depends_on = module.maps3_initialize.s3_id
}

module "dev_appserver" {
    source = "../../resources/ec2"
    ami = "ami-0a243dbef00e96192"
    instanceType = "t3.micro"
    subnetId = "subnet-0444f510ec8f7d2a8"
    name = "appserver"
    appMigrationedId = module.dev_appserver_maplambda.mapServerId
    serverMigratedId = module.dev_appserver_maplambda.mapAppId
    migrationProjectId = var.migrationProjectId
}
#--------------------