resource "aws_lambda_permission" "with_sns" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.sns_listener.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = data.aws_ssm_parameter.sns_nmap_topic_arn.value
}

resource "aws_sns_topic_subscription" "lambda" {
  topic_arn = data.aws_ssm_parameter.sns_nmap_topic_arn.value
  protocol  = "lambda"
  endpoint  = aws_lambda_function.sns_listener.arn
}

data "aws_iam_policy_document" "sns_sqs_policy" {
  statement {
    actions   = ["SQS:SendMessage"]
    effect    = "Allow"
    resources = ["*"]
  }
}

resource "aws_iam_policy" "sns_sqs_policy" {
  name   = "${terraform.workspace}-${var.app_name}-${var.task_name}-task-sqstrigger"
  policy = data.aws_iam_policy_document.sns_sqs_policy.json
}

resource "aws_iam_role_policy_attachment" "sns_sqs_policy" {
  role       = var.task_queue_consumer_role
  policy_arn = aws_iam_policy.sns_sqs_policy.arn
}

resource "aws_lambda_function" "sns_listener" {
  depends_on       = [data.external.ssl_zip]
  function_name    = "${terraform.workspace}-${var.app_name}-${var.task_name}-sns-listener"
  handler          = "sns_listener.sns_listener.check_event"
  role             = var.task_queue_consumer_arn
  runtime          = "python3.7"
  filename         = local.ssl_zip
  source_code_hash = data.external.ssl_zip.result.hash

  layers = [
    data.aws_ssm_parameter.utils_layer.value,
  ]

  environment {
    variables = {
      REGION    = var.aws_region
      STAGE     = terraform.workspace
      APP_NAME  = var.app_name
      TASK_NAME = var.task_name
    }
  }

  tags = {
    workspace = terraform.workspace
    app_name  = var.app_name
  }
}

