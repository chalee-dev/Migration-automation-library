output "mapServerId" {
    value = jsondecode(jsondecode(data.aws_lambda_invocation.example_lambda_func.result)["body"])["aws-migrated"]
}

output "mapAppId" {
    value = jsondecode(jsondecode(data.aws_lambda_invocation.example_lambda_func.result)["body"])["aws-migrated-app"]
}
