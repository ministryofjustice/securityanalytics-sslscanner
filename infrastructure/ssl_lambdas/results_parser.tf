resource "aws_lambda_permission" "s3_invoke" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.results_parser.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = var.results_bucket_arn
}

resource "aws_s3_bucket_notification" "ingestor_queue_trigger" {
  depends_on = [aws_lambda_permission.s3_invoke]
  bucket     = var.results_bucket

  lambda_function {
    lambda_function_arn = aws_lambda_function.results_parser.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".tar.gz"
  }
}

resource "aws_lambda_function" "results_parser" {
  depends_on = [data.external.ssl_zip]

  function_name    = "${terraform.workspace}-${var.app_name}-${var.task_name}-results-parser"
  handler          = "results_parser.results_parser.parse_results"
  role             = var.results_parser_role
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

