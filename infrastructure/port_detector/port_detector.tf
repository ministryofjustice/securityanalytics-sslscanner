resource "aws_lambda_permission" "with_sns" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.port_detector.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = data.aws_ssm_parameter.sns_nmap_results_topic_arn.value
}

resource "aws_sns_topic_subscription" "subscribe_to_nmap_outputs" {
  topic_arn = data.aws_ssm_parameter.sns_nmap_results_topic_arn.value
  protocol  = "lambda"
  endpoint  = aws_lambda_function.port_detector.arn
}

module "port_detector_dead_letters" {
  source = "github.com/ministryofjustice/securityanalytics-sharedcode//infrastructure/dead_letter_recorder"
  # source = "../../../securityanalytics-sharedcode/infrastructure/dead_letter_recorder"
  aws_region       = var.aws_region
  app_name         = var.app_name
  account_id       = var.account_id
  ssm_source_stage = var.ssm_source_stage
  use_xray         = var.use_xray
  recorder_name    = "port-detector-DLQ"
  s3_bucket        = data.aws_ssm_parameter.dead_letter_bucket_name.value
  s3_bucket_arn    = data.aws_ssm_parameter.dead_letter_bucket_arn.value
  s3_key_prefix    = "port-detector"
  source_arn       = aws_lambda_function.port_detector.arn
}

resource "aws_lambda_function" "port_detector" {
  depends_on       = [var.ssl_zip]
  function_name    = "${terraform.workspace}-${var.app_name}-port-detector"
  handler          = "port_detector.invoke"
  role             = aws_iam_role.port_detector.arn
  runtime          = "python3.7"
  filename         = var.ssl_zip
  source_code_hash = filebase64sha256(var.ssl_zip)
  timeout          = 10

  layers = [
    data.aws_ssm_parameter.utils_layer.value,
    data.aws_ssm_parameter.tasks_layer.value,
  ]

  dead_letter_config {
    target_arn = module.port_detector_dead_letters.arn
  }

  environment {
    variables = {
      REGION    = var.aws_region
      STAGE     = terraform.workspace
      APP_NAME  = var.app_name
      GLUE_NAME = "port_detector"
    }
  }

  tags = {
    workspace = terraform.workspace
    app_name  = var.app_name
  }
}

