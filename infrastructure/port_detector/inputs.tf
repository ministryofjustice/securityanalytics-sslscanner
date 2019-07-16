variable "app_name" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "account_id" {
}

variable "ssm_source_stage" {
  type        = string
  description = "When deploying infrastructure for integration tests the source of ssm parameters for e.g. the congnito pool need to come from dev, not from the stage with the same name."
}

variable "transient_workspace" {
  type        = string
  description = "Used when doing integration tests to make the results buckets created deleteable."
}

variable "use_xray" {
  type        = string
  description = "Whether to instrument lambdas"
}

variable "ssl_zip" {
  type = string
}

variable "results_topic_arn" {
  type = string
}