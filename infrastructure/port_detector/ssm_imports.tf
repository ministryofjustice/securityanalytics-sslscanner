data "aws_ssm_parameter" "utils_layer" {
  name = "/${var.app_name}/${var.ssm_source_stage}/lambda/layers/utils/arn"
}

data "aws_ssm_parameter" "tasks_layer" {
  name = "/${var.app_name}/${var.ssm_source_stage}/lambda/layers/shared_task_code/arn"
}

data "aws_ssm_parameter" "dead_letter_bucket_name" {
  name = "/${var.app_name}/${var.ssm_source_stage}/s3/dead_letters/name"
}

data "aws_ssm_parameter" "dead_letter_bucket_arn" {
  name = "/${var.app_name}/${var.ssm_source_stage}/s3/dead_letters/arn"
}

data "aws_ssm_parameter" "nmap_results_topic_arn" {
  name = "/${var.app_name}/${var.ssm_source_stage}/tasks/nmap/results/arn"

}
