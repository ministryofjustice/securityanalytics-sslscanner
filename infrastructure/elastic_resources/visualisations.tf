module "root_ca_distro" {
  # two slashes are intentional: https://www.terraform.io/docs/modules/sources.html#modules-in-package-sub-directories
  source = "github.com/ministryofjustice/securityanalytics-analyticsplatform//infrastructure/kibana_saved_object"

  # It is sometimes useful for the developers of the project to use a local version of the task
  # execution project. This enables them to develop the task execution project and the nmap scanner
  # (or other future tasks), at the same time, without requiring the task execution changes to be
  # pushed to master. Unfortunately you can not interpolate variables to generate source locations, so
  # devs will have to comment in/out this line as and when they need
  #  source = "../../../securityanalytics-analyticsplatform/infrastructure/kibana_saved_object"
  app_name = var.app_name

  aws_region       = var.aws_region
  ssm_source_stage = var.ssm_source_stage
  object_template  = "${path.module}/visualisations/root_ca/root_ca_distro.vis.json"

  object_substitutions = {
    index     = module.index_pattern_data_snapshot.object_id
    search_id = module.root_ca_search.object_id
  }

  object_type  = "visualization"
  object_title = "Distribution of Root CAs"
  es_domain    = data.aws_ssm_parameter.es_domain.value
}

module "cert_chain_errors_distro" {
  # two slashes are intentional: https://www.terraform.io/docs/modules/sources.html#modules-in-package-sub-directories
  source = "github.com/ministryofjustice/securityanalytics-analyticsplatform//infrastructure/kibana_saved_object"

  # It is sometimes useful for the developers of the project to use a local version of the task
  # execution project. This enables them to develop the task execution project and the nmap scanner
  # (or other future tasks), at the same time, without requiring the task execution changes to be
  # pushed to master. Unfortunately you can not interpolate variables to generate source locations, so
  # devs will have to comment in/out this line as and when they need
  #  source = "../../../securityanalytics-analyticsplatform/infrastructure/kibana_saved_object"
  app_name = var.app_name

  aws_region       = var.aws_region
  ssm_source_stage = var.ssm_source_stage
  object_template  = "${path.module}/visualisations/cert_chain_errors/cert_chain_errors_distro.vis.json"

  object_substitutions = {
    index     = module.index_pattern_data_snapshot.object_id
    search_id = module.cert_chain_errors_search.object_id
  }

  object_type  = "visualization"
  object_title = "SSL cert chain errors"
  es_domain    = data.aws_ssm_parameter.es_domain.value
}

module "cert_chain_errors_table" {
  # two slashes are intentional: https://www.terraform.io/docs/modules/sources.html#modules-in-package-sub-directories
  source = "github.com/ministryofjustice/securityanalytics-analyticsplatform//infrastructure/kibana_saved_object"

  # It is sometimes useful for the developers of the project to use a local version of the task
  # execution project. This enables them to develop the task execution project and the nmap scanner
  # (or other future tasks), at the same time, without requiring the task execution changes to be
  # pushed to master. Unfortunately you can not interpolate variables to generate source locations, so
  # devs will have to comment in/out this line as and when they need
  #  source = "../../../securityanalytics-analyticsplatform/infrastructure/kibana_saved_object"
  app_name = var.app_name

  aws_region       = var.aws_region
  ssm_source_stage = var.ssm_source_stage
  object_template  = "${path.module}/visualisations/cert_chain_errors/cert_chain_errors_table.vis.json"

  object_substitutions = {
    index     = module.index_pattern_data_snapshot.object_id
    search_id = module.cert_chain_errors_search.object_id
  }

  object_type  = "visualization"
  object_title = "SSL cert chain errors table"
  es_domain    = data.aws_ssm_parameter.es_domain.value
}



module "ai_cert_chain_errors_filter" {
  # two slashes are intentional: https://www.terraform.io/docs/modules/sources.html#modules-in-package-sub-directories
  source = "github.com/ministryofjustice/securityanalytics-analyticsplatform//infrastructure/kibana_saved_object"

  # It is sometimes useful for the developers of the project to use a local version of the task
  # execution project. This enables them to develop the task execution project and the nmap scanner
  # (or other future tasks), at the same time, without requiring the task execution changes to be
  # pushed to master. Unfortunately you can not interpolate variables to generate source locations, so
  # devs will have to comment in/out this line as and when they need
  # source = "../../../securityanalytics-analyticsplatform/infrastructure/kibana_saved_object"
  app_name = var.app_name

  aws_region       = var.aws_region
  ssm_source_stage = var.ssm_source_stage
  object_template  = "${path.module}/visualisations/cert_chain_errors/ai_cert_chain_errors_filter.vis.json"

  object_substitutions = {
    index = module.index_pattern_data_snapshot.object_id

  }

  object_type  = "visualization"
  object_title = "SSL cert chain errors filter"
  es_domain    = data.aws_ssm_parameter.es_domain.value
}


module "ai_cert_chain_errors_table" {
  # two slashes are intentional: https://www.terraform.io/docs/modules/sources.html#modules-in-package-sub-directories
  source = "github.com/ministryofjustice/securityanalytics-analyticsplatform//infrastructure/kibana_saved_object"

  # It is sometimes useful for the developers of the project to use a local version of the task
  # execution project. This enables them to develop the task execution project and the nmap scanner
  # (or other future tasks), at the same time, without requiring the task execution changes to be
  # pushed to master. Unfortunately you can not interpolate variables to generate source locations, so
  # devs will have to comment in/out this line as and when they need
  # source = "../../../securityanalytics-analyticsplatform/infrastructure/kibana_saved_object"
  app_name = var.app_name

  aws_region       = var.aws_region
  ssm_source_stage = var.ssm_source_stage
  object_template  = "${path.module}/visualisations/cert_chain_errors/ai_cert_chain_errors_table.vis.json"

  object_substitutions = {
    index = module.index_pattern_data_snapshot.object_id

  }

  object_type  = "visualization"
  object_title = "SSL cert chain errors table"
  es_domain    = data.aws_ssm_parameter.es_domain.value
}
