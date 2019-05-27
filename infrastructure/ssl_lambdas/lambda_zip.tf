locals {
  ssl_zip = "../.generated/sec-an-ssl.zip"
}

data "external" "ssl_zip" {
  program = [
    "python",
    "../shared_code/python/package_lambda.py",
    "${local.ssl_zip}",
    "${path.module}/packaging.config.json",
    "../Pipfile.lock",
  ]
}
