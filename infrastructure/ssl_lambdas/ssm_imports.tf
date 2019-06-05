data "aws_ssm_parameter" "utils_layer" {
  name = "/${var.app_name}/${var.ssm_source_stage}/lambda/layers/utils/arn"
}

data "aws_ssm_parameter" "api_gateway" {
  name = "/${var.app_name}/${var.ssm_source_stage}/api/private/name"
}

data "aws_ssm_parameter" "sns_nmap_topic_arn" {
  name = "/${var.app_name}/${terraform.workspace}/tasks/nmap/results/arn"
}

