resource "aws_ssm_parameter" "port_notifier" {
  name        = "/${var.app_name}/${terraform.workspace}/glue/port_detector/sns_target"
  description = "The results broadcaster"
  type        = "String"
  value       = aws_sns_topic.detected_ports.arn
  overwrite   = "true"

  tags = {
    app_name  = var.app_name
    workspace = terraform.workspace
  }
}