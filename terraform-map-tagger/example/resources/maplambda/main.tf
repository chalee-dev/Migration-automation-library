#*********************
# Call the lambda function to get the MAP tags for the given hostname
data "aws_lambda_invocation" "example_lambda_func" {
    function_name   = "getMapTagsForHost"

    input = <<JSON
    {
        "hostName": "${var.hostName}",
        "appName": "${var.appName}",
        "bucketName": "${var.bucketName}",
        "migrationHubServerFileName": "${var.migrationHubServerFileName}",
        "migrationHubAppFileName": "${var.migrationHubAppFileName}"
    }
    JSON

    depends_on = [var.target_group_depends_on]
}
#--------------------