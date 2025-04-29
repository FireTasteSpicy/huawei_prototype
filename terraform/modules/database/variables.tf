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

# Network Variables
variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
}

variable "db_subnet_id" {
  description = "ID of the database subnet"
  type        = string
}

variable "db_security_group_id" {
  description = "ID of the database security group"
  type        = string
}

variable "app_security_group_id" {
  description = "ID of the application security group"
  type        = string
}

# Security Variables
variable "postgres_password" {
  description = "Password for PostgreSQL database"
  type        = string
  sensitive   = true
}

variable "redis_password" {
  description = "Password for Redis cache"
  type        = string
  sensitive   = true
}

variable "kms_key_id" {
  description = "KMS key ID for encryption"
  type        = string
}

# PostgreSQL Configuration
variable "postgres_instance_name" {
  description = "Name for PostgreSQL instance"
  type        = string
  default     = null
}

variable "postgres_instance_type" {
  description = "Instance type for PostgreSQL"
  type        = string
  default     = "rds.pg.n1.large.2" # 2vCPUs, 8GB RAM
}

variable "postgres_db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "app_db"
}

variable "postgres_username" {
  description = "PostgreSQL admin username"
  type        = string
  default     = "postgres_admin"
}

variable "postgres_storage_type" {
  description = "Storage type for PostgreSQL"
  type        = string
  default     = "ULTRAHIGH" # High-performance SSD
}

variable "postgres_storage_size" {
  description = "Storage size in GB for PostgreSQL"
  type        = number
  default     = 40
}

variable "postgres_version" {
  description = "PostgreSQL version"
  type        = string
  default     = "14"
}

# Redis Configuration
variable "redis_instance_name" {
  description = "Name for Redis instance"
  type        = string
  default     = null
}

variable "redis_instance_type" {
  description = "Instance type for Redis"
  type        = string
  default     = "redis.ha.xu1.large.r2.2" # 2GB memory
}

variable "redis_version" {
  description = "Redis version"
  type        = string
  default     = "5.0"
}