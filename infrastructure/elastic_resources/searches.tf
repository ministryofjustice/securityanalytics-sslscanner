module "root_ca_search" {
  # two slashes are intentional: https://www.terraform.io/docs/modules/sources.html#modules-in-package-sub-directories
  source = "github.com/ministryofjustice/securityanalytics-analyticsplatform//infrastructure/kibana_saved_object"

  #  source = "../../../securityanalytics-analyticsplatform/infrastructure/kibana_saved_object"
  app_name = var.app_name

  aws_region       = var.aws_region
  ssm_source_stage = var.ssm_source_stage
  object_template  = "${path.module}/searches/root_ca.search.json"

  object_substitutions = {
    index = module.index_pattern_data_snapshot.object_id
  }

  object_type  = "search"
  object_title = "RootCA for SSL hosts"
  es_domain    = data.aws_ssm_parameter.es_domain.value
}

module "cert_chain_errors_search" {
  # two slashes are intentional: https://www.terraform.io/docs/modules/sources.html#modules-in-package-sub-directories
  source = "github.com/ministryofjustice/securityanalytics-analyticsplatform//infrastructure/kibana_saved_object"

  #  source = "../../../securityanalytics-analyticsplatform/infrastructure/kibana_saved_object"
  app_name = var.app_name

  aws_region       = var.aws_region
  ssm_source_stage = var.ssm_source_stage
  object_template  = "${path.module}/searches/cert_chain_errors.search.json"

  object_substitutions = {
    index = module.index_pattern_data_snapshot.object_id
  }

  object_type  = "search"
  object_title = "SSL cert chain errors"
  es_domain    = data.aws_ssm_parameter.es_domain.value
}


