data "aws_iam_role" "sns_logging" {
  name = "${var.ssm_source_stage}-${var.app_name}-sns-logging"
}

resource "aws_sns_topic" "detected_ports" {
  name         = "${terraform.workspace}-${var.app_name}-ports-detected"
  display_name = "SNS topic to distribute detected ports"

  sqs_failure_feedback_role_arn    = data.aws_iam_role.sns_logging.arn
  sqs_success_feedback_role_arn    = data.aws_iam_role.sns_logging.arn
  sqs_success_feedback_sample_rate = 5
  # TODO enable sns encryption
  # kms_master_key_id = "aws/sns"
}

