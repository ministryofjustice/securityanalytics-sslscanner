variable "aws_region" {
  type = "string"
}

variable "app_name" {
  type = "string"
}

variable "task_name" {
  type = "string"
}

variable "ssm_source_stage" {
  type        = "string"
  description = "When deploying infrastructure for integration tests the source of ssm parameters for e.g. the congnito pool need to come from dev, not from the stage with the same name."
}
