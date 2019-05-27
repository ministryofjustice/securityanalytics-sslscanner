#!/usr/bin/sh

. ./.venv/bin/activate
export AWS_REGION=eu-west-2
export PYTHONPATH=`pwd`
export PYTHONPATH=$PYTHONPATH:`pwd`/shared_code/python
export USERNAME=builder

# Get short version of git hash for temporary deployment
export SOURCE_VERSION=`git rev-parse HEAD`
export DEPLOY_STAGE=$(expr substr $SOURCE_VERSION 1 8)

# TODO change this when we have more stages than just dev
export SSM_SOURCE_STAGE=dev