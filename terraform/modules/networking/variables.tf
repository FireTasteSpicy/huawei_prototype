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

# VPC Variables
variable "vpc_name" {
  description = "Name of the VPC"
  default     = "huawei-prototype-vpc"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  default     = "10.0.0.0/16"
}

# Subnet Variables
variable "web_subnet_cidr" {
  description = "CIDR block for the web tier subnet"
  default     = "10.0.1.0/24"
}

variable "app_subnet_cidr" {
  description = "CIDR block for the application tier subnet"
  default     = "10.0.2.0/24"
}

variable "db_subnet_cidr" {
  description = "CIDR block for the database tier subnet"
  default     = "10.0.3.0/24"
}

variable "management_subnet_cidr" {
  description = "CIDR block for the management subnet"
  default     = "10.0.4.0/24"
}

# Availability Zones
variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["ap-southeast-3a", "ap-southeast-3b"]
}

# Security Group Variables
variable "admin_ip_addresses" {
  description = "List of admin IP addresses allowed for SSH access"
  type        = list(string)
  default     = ["0.0.0.0/0"] # Replace with your actual IP addresses for security
}