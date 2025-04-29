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

# OBS Bucket Variables
variable "logs_bucket_name" {
  description = "Name of the bucket for storing logs"
  type        = string
  default     = null # Will be auto-generated if not specified
}

variable "artifacts_bucket_name" {
  description = "Name of the bucket for storing application artifacts"
  type        = string
  default     = null
}

variable "static_assets_bucket_name" {
  description = "Name of the bucket for storing static website assets"
  type        = string
  default     = null
}

variable "backups_bucket_name" {
  description = "Name of the bucket for storing backups"
  type        = string
  default     = null
}