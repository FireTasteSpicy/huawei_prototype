# Authentication Variables
variable "region" {
  description = "Huawei Cloud region"
  type        = string
  default     = "ap-southeast-3" # Singapore region
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
  default     = "huawei-prototype"
}

variable "admin_ip_addresses" {
  description = "List of IP addresses allowed for admin access"
  type        = list(string)
  default     = ["39.109.141.20/32"]
}