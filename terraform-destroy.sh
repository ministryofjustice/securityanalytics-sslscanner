#!/bin/sh

cd infrastructure
terraform init -backend-config "bucket=$1-terraform-state"
terraform workspace new $2 || terraform workspace select $2
terraform destroy -auto-approve -input=true -var app_name=$1
# pause in case the user is watching output
sleep 5