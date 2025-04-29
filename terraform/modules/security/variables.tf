# Authentication Variables
variable "region" {
  description = "Huawei Cloud region"
  type        = string
}

variable "access_key" {
  description = "Huawei Cloud access key"
  type        = string
  sensitive   = true
}

variable "secret_key" {
  description = "Huawei Cloud secret key"
  type        = string
  sensitive   = true
}

# Project Variables
variable "project_name" {
  description = "Name of the project for resource naming"
  type        = string
}

# KMS Variables
variable "kms_key_alias" {
  description = "Alias for the KMS key"
  type        = string
  default     = "app-secrets-key"
}