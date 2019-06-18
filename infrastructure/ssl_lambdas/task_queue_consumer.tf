resource "aws_lambda_permission" "sqs_invoke" {
  statement_id  = "AllowExecutionFromSQS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.queue_consumer.function_name
  principal     = "sqs.amazonaws.com"
  source_arn    = var.queue_arn
}

resource "aws_lambda_event_source_mapping" "ingestor_queue_trigger" {
  depends_on       = [aws_lambda_permission.sqs_invoke]
  event_source_arn = var.queue_arn
  function_name    = aws_lambda_function.queue_consumer.arn
  enabled          = true
  batch_size       = 1
}

resource "aws_iam_role_policy_attachment" "task_qpolicy" {
  role       = var.task_queue_consumer_role
  policy_arn = var.s3_bucket_policy_arn
}

resource "aws_lambda_function" "queue_consumer" {
  depends_on = [data.external.ssl_zip]

  function_name    = "${terraform.workspace}-${var.app_name}-${var.task_name}-task-q-consumer"
  handler          = "task_queue_consumer.task_queue_consumer.submit_scan_task"
  role             = var.task_queue_consumer_arn
  runtime          = "python3.7"
  filename         = local.ssl_zip
  source_code_hash = data.external.ssl_zip.result.hash
  timeout          = 30

  layers = [
    data.aws_ssm_parameter.utils_layer.value,
    data.aws_ssm_parameter.shared_task_code_layer.value,
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

