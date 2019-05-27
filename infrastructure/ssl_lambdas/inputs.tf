variable "app_name" {
  type = "string"
}

variable "task_name" {
  type = "string"
}

variable "aws_region" {
  type = "string"
}

variable "account_id" {
  type = "string"
}

variable "queue_arn" {
  type = "string"
}

variable "task_queue_consumer_arn" {
  type = "string"
}

variable "task_queue_consumer_role" {
  type = "string"
}

variable "results_bucket" {
  type = "string"
}

variable "results_bucket_arn" {
  type = "string"
}

variable "results_parser_role" {
  type = "string"
}

variable "ssm_source_stage" {
  type = "string"
}

variable "s3_bucket_policy_arn" {
  type = "string"
}

variable "s3_bucket_policy_doc" {
  type = "string"
}
