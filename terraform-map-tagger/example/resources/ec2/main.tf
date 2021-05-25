resource "aws_instance" "example-ec2" {
  ami           = var.ami
  instance_type = var.instanceType
  subnet_id     = var.subnetId
  tags          = {
      Name                      = var.name
      aws-migration-project-id  = var.migrationProjectId
      map-migrated              = var.serverMigratedId
      map-migrated-app          = var.appMigrationedId
  }
}

