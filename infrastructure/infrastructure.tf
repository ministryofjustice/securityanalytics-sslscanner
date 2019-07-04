#############################################
# Backend setup
#############################################

terraform {
  backend "s3" {
    # This is configured using the -backend-config parameter with 'terraform init'
    bucket         = ""
    dynamodb_table = "sec-an-terraform-locks"
    key            = "ssl/terraform.tfstate"
    region         = "eu-west-2" # london
    profile        = "sec-an"
  }
}

#############################################
# Variables used across the whole application
#############################################

variable "aws_region" {
  default = "eu-west-2" # london
}

# Set this variable with your app.auto.tfvars file or enter it manually when prompted
variable "app_name" {
}

variable "task_name" {
  default = "ssl"
}

variable "account_id" {
}

variable "ssm_source_stage" {
  default = "DEFAULT"
}

variable "known_deployment_stages" {
  type    = list(string)
  default = ["dev", "qa", "prod"]
}

variable "use_xray" {
  type        = string
  description = "Whether to instrument lambdas"
  default     = false
}

provider "aws" {
  version             = "~> 2.13"
  region              = var.aws_region
  profile             = var.app_name
  allowed_account_ids = [var.account_id]
}

#############################################
# Resources
#############################################

locals {
  # When a build is done as a user locally, or when building a stage e.g. dev/qa/prod we use
  # the workspace name e.g. progers or dev
  # When the circle ci build is run we override the var.ssm_source_stage to explicitly tell it
  # to use the resources in dev. Change
  ssm_source_stage = var.ssm_source_stage == "DEFAULT" ? terraform.workspace : var.ssm_source_stage

  transient_workspace = false == contains(var.known_deployment_stages, terraform.workspace)
}


locals {
  ssl_zip = "../.generated/sec-an-ssl.zip"
}

data "external" "ssl_zip" {
  program = [
    "python",
    "../shared_code/python/package_lambda.py",
    "-x",
    local.ssl_zip,
    "${path.module}/packaging.config.json",
    "../Pipfile.lock",
  ]
}


# TODO This module doesn't belong in the ssl scan, most of the secondary scans require it's input
module "port_detector" {
  source = "./port_detector"

  account_id = var.account_id
  aws_region          = var.aws_region
  app_name            = var.app_name
  use_xray            = var.use_xray
  transient_workspace = local.transient_workspace
  ssm_source_stage    = local.ssm_source_stage

  ssl_zip       = local.ssl_zip
}

locals {
  port_443_filter_policy = {
     "port_id": ["443"],
  }
  # To avoid scanning port 443 twice exclude it from this second subscription
  service_https_filter_policy = {
     "service": ["https"],
     "port_id":  [{"anything-but": "443"}]
  }
}

# connect the ssl scanner to the port detector
resource "aws_sns_topic_subscription" "subscribe_ssl_to_port_443" {
  topic_arn            = module.port_detector.notifier
  protocol             = "sqs"
  endpoint             = module.ssl_task.task_queue
  raw_message_delivery = false
  filter_policy = jsonencode(local.port_443_filter_policy)
}

# connect the ssl scanner to the port detector
resource "aws_sns_topic_subscription" "subscribe_ssl_to_service_https" {
  topic_arn            = module.port_detector.notifier
  protocol             = "sqs"
  endpoint             = module.ssl_task.task_queue
  raw_message_delivery = false
  filter_policy = jsonencode(local.service_https_filter_policy)
}

module "ssl_task" {
  source = "../../securityanalytics-taskexecution/infrastructure/lambda_task"

  account_id          = var.account_id
  aws_region          = var.aws_region
  app_name            = var.app_name
  task_name           = var.task_name
  use_xray            = var.use_xray
  transient_workspace = local.transient_workspace
  ssm_source_stage    = local.ssm_source_stage

  # TODO add separate settings for results and scan lambdas
  cpu    = "1024"
  memory = "2048"

  scan_lambda = "ssl_scanner.invoke"

  # Results
  lambda_zip           = local.ssl_zip
  results_parse_lambda = "results_parser.invoke"

  # General
  subscribe_input_to_scan_initiator = false
  subscribe_es_to_output            = true
}

module "elastic_resources" {
  source           = "./elastic_resources"
  aws_region       = var.aws_region
  app_name         = var.app_name
  task_name        = var.task_name
  ssm_source_stage = local.ssm_source_stage
}

