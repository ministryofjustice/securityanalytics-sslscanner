data "aws_ssm_parameter" "es_domain" {
  name = "/${var.app_name}/${var.ssm_source_stage}/analytics/elastic/es_endpoint/url"
}
