# Networking Module - Core infrastructure
module "networking" {
  source       = "./modules/networking"
  
  region       = var.region
  access_key   = var.access_key
  secret_key   = var.secret_key
  project_name = var.project_name
  
  providers = {
    huaweicloud = huaweicloud
  }
}

# Storage Module - OBS Buckets
module "storage" {
  source       = "./modules/storage"
  
  region       = var.region
  access_key   = var.access_key
  secret_key   = var.secret_key
  project_name = var.project_name
  
  providers = {
    huaweicloud = huaweicloud
  }
}

# Security Module - KMS and Secrets
module "security" {
  source       = "./modules/security"
  
  region       = var.region
  access_key   = var.access_key
  secret_key   = var.secret_key
  project_name = var.project_name
  
  providers = {
    huaweicloud = huaweicloud
  }
}

# Database Module - RDS PostgreSQL and Redis Cache
module "database" {
  source       = "./modules/database"
  
  region       = var.region
  access_key   = var.access_key
  secret_key   = var.secret_key
  project_name = var.project_name
  
  # Network dependencies
  vpc_id              = module.networking.vpc_id
  db_subnet_id        = module.networking.db_subnet_id
  db_security_group_id = module.networking.db_security_group_id
  app_security_group_id = module.networking.app_security_group_id
  
  # Secret dependencies
  postgres_password = module.security.postgres_password
  redis_password    = module.security.redis_password
  kms_key_id        = module.security.kms_key_id
  
  # Only create after security module is ready
  depends_on = [module.security, module.networking]
  
  providers = {
    huaweicloud = huaweicloud
  }
}