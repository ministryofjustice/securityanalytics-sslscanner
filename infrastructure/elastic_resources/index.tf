# data "local_file" "index_definition" {
#   filename = "${path.module}/ssl-data.index.json"
# }
# data "external" "current_index" {
#   program = [
#     "python",
#     "${path.module}/get-current-write-index.py",
#     "${var.aws_region}",
#     "${var.app_name}",
#     "${var.task_name}",
#     "${data.aws_ssm_parameter.es_domain.value}",
#   ]
# }
# locals {
#   index_hash     = "${md5(data.local_file.index_definition.content)}"
#   script_hash    = "${md5(file("${path.module}/write-new-index.py"))}"
#   old_index_hash = "${data.external.current_index.result.index}"
# }
# resource "null_resource" "setup_new_index" {
#   # This count stops us from re-indexing dev, when looking at integration tests
#   count = "${var.ssm_source_stage == terraform.workspace ? 1 : 0}"
#   triggers {
#     index_hash  = "${local.index_hash}"
#     script_hash = "${local.script_hash}"
#   }
#   provisioner "local-exec" {
#     # Doesn't just write the new one, it also updates the aliases and starts re-indexing
#     command = "python ${path.module}/write-new-index.py ${var.aws_region} ${var.app_name} ${var.task_name} ${local.index_hash} ${data.local_file.index_definition.filename} ${data.aws_ssm_parameter.es_domain.value} ${local.old_index_hash}"
#   }
# }

