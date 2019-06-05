module "root_ca_distro" {
  // two slashes are intentional: https://www.terraform.io/docs/modules/sources.html#modules-in-package-sub-directories
  source = "github.com/ministryofjustice/securityanalytics-analyticsplatform//infrastructure/kibana_saved_object"

  // It is sometimes useful for the developers of the project to use a local version of the task
  // execution project. This enables them to develop the task execution project and the nmap scanner
  // (or other future tasks), at the same time, without requiring the task execution changes to be
  // pushed to master. Unfortunately you can not interpolate variables to generate source locations, so
  // devs will have to comment in/out this line as and when they need
  //  source = "../../../securityanalytics-analyticsplatform/infrastructure/kibana_saved_object"
  app_name = var.app_name

  aws_region       = var.aws_region
  ssm_source_stage = var.ssm_source_stage
  task_name        = var.task_name
  object_template  = "${path.module}/visualisations/root_ca/root_ca_distro.vis.json"

  object_substitutions = {
    index     = module.index_pattern_data_snapshot.object_id
    search_id = module.root_ca_search.object_id
  }

  object_type  = "visualization"
  object_title = "Distribution of Root CAs"
}

