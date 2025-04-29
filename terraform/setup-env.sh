#!/bin/bash

# Load environment variables from .env file
set -a
source ../.env
set +a

# Export as Terraform variables
export TF_VAR_access_key="${HUAWEI_ACCESS_KEY}"
export TF_VAR_secret_key="${HUAWEI_SECRET_ACCESS_KEY}"

echo "Environment variables set for Terraform"