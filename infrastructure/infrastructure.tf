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

provider "aws" {
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
}

module "elastic_resources" {
  # TF-UPGRADE-TODO: In Terraform v0.11 and earlier, it was possible to
  # reference a relative module source without a preceding ./, but it is no
  # longer supported in Terraform v0.12.
  #
  # If the below module source is indeed a relative local path, add ./ to the
  # start of the source string. If that is not the case, then leave it as-is
  # and remove this TODO comment.
  source           = "./elastic_resources"
  aws_region       = var.aws_region
  app_name         = var.app_name
  task_name        = var.task_name
  ssm_source_stage = local.ssm_source_stage
}

module "ssl_task" {
  // two slashes are intentional: https://www.terraform.io/docs/modules/sources.html#modules-in-package-sub-directories  

  source = "github.com/ministryofjustice/securityanalytics-taskexecution//infrastructure/task"

  // It is sometimes useful for the developers of the project to use a local version of the task  // execution project. This enables them to develop the task execution project and the ssl scanner  // (or other future tasks), at the same time, without requiring the task execution changes to be  // pushed to master. Unfortunately you can not interpolate variables to generate source locations, so  // devs will have to comment in/out this line as and when they need

  #source = "../../securityanalytics-taskexecution/infrastructure/task"

  app_name                      = var.app_name
  aws_region                    = var.aws_region
  task_name                     = var.task_name
  subscribe_elastic_to_notifier = true
  account_id                    = var.account_id
  ssm_source_stage              = local.ssm_source_stage
  transient_workspace           = false == contains(var.known_deployment_stages, terraform.workspace)
}

module "openssl" {
  # TF-UPGRADE-TODO: In Terraform v0.11 and earlier, it was possible to
  # reference a relative module source without a preceding ./, but it is no
  # longer supported in Terraform v0.12.
  #
  # If the below module source is indeed a relative local path, add ./ to the
  # start of the source string. If that is not the case, then leave it as-is
  # and remove this TODO comment.
  source                   = "./ssl_lambdas"
  app_name                 = var.app_name
  task_name                = var.task_name
  results_bucket           = module.ssl_task.results_bucket_id
  results_bucket_arn       = module.ssl_task.results_bucket_arn
  aws_region               = var.aws_region
  account_id               = var.account_id
  queue_arn                = module.ssl_task.task_queue
  ssm_source_stage         = local.ssm_source_stage
  task_queue_consumer_arn  = module.ssl_task.task_queue_consumer_arn
  task_queue_consumer_role = module.ssl_task.task_queue_consumer_role
  results_parser_role      = module.ssl_task.results_parser
  s3_bucket_policy_arn     = module.ssl_task.s3_bucket_policy_arn
  s3_bucket_policy_doc     = module.ssl_task.s3_bucket_policy_doc
}

