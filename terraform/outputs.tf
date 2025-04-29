// Update the existing file ~/workspace/huawei_prototype/terraform/outputs.tf
# Networking outputs
output "vpc" {
  description = "Details about the created VPC"
  value = {
    id          = module.networking.vpc_id
    web_subnet  = module.networking.web_subnet_id
    app_subnet  = module.networking.app_subnet_id
    db_subnet   = module.networking.db_subnet_id
    mgmt_subnet = module.networking.management_subnet_id
  }
}

output "security_groups" {
  description = "Security group IDs"
  value = {
    web        = module.networking.web_security_group_id
    app        = module.networking.app_security_group_id
    database   = module.networking.db_security_group_id
    management = module.networking.management_security_group_id
  }
}

output "nat_gateway" {
  description = "NAT Gateway details"
  value = {
    id       = module.networking.nat_gateway_id
    public_ip = module.networking.nat_gateway_eip
  }
}

# Storage outputs
output "obs_buckets" {
  description = "Information about created OBS buckets"
  value = {
    logs_bucket         = module.storage.logs_bucket
    artifacts_bucket    = module.storage.artifacts_bucket
    static_assets_bucket = module.storage.static_assets_bucket
    backups_bucket      = module.storage.backups_bucket
  }
}

# Security outputs
output "kms_key_id" {
  description = "KMS key ID used for encryption"
  value       = module.security.kms_key_id
}

output "secret_names" {
  description = "Names of created secrets"
  value = {
    postgres_secret = module.security.postgres_secret_name
    redis_secret    = module.security.redis_secret_name
  }
}

# Database outputs
output "postgres_instance" {
  description = "PostgreSQL instance details"
  value = {
    id       = module.database.rds_instance_id
    endpoint = module.database.rds_instance_endpoint
    port     = module.database.rds_instance_port
  }
}

output "redis_instance" {
  description = "Redis instance details"
  value = {
    id       = module.database.redis_instance_id
    ip       = module.database.redis_instance_ip
    port     = module.database.redis_instance_port
  }
}