locals {
  postgres_instance_name = var.postgres_instance_name != null ? var.postgres_instance_name : "${var.project_name}-postgres"
  redis_instance_name = var.redis_instance_name != null ? var.redis_instance_name : "${var.project_name}-redis"
}

# PostgreSQL RDS Instance
resource "huaweicloud_rds_instance" "postgres" {
  name              = local.postgres_instance_name
  flavor            = var.postgres_instance_type
  vpc_id            = var.vpc_id
  subnet_id         = var.db_subnet_id
  security_group_id = var.db_security_group_id
  
  availability_zone = ["ap-southeast-3a"]
  
  db {
    type     = "PostgreSQL"
    version  = var.postgres_version
    password = var.postgres_password
    port     = 5432
  }
  
  volume {
    type = "COMMON"
    size = var.postgres_storage_size
  }
  
  backup_strategy {
    start_time = "03:00-04:00"
    keep_days  = 7
  }
  
  tags = {
    Name        = "${var.project_name}-postgres"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Create database within PostgreSQL instance
resource "huaweicloud_rds_database" "app_database" {
  instance_id   = huaweicloud_rds_instance.postgres.id
  name          = var.postgres_db_name
  character_set = "UTF8"
  description   = "Main database for ${var.project_name} application"
}

resource "huaweicloud_dcs_instance" "redis" {
  name               = local.redis_instance_name
  engine             = "Redis"
  engine_version     = var.redis_version
  capacity           = 2  # Size in GB
  vpc_id             = var.vpc_id
  subnet_id          = var.db_subnet_id
  # Remove security_group_id and add whitelists
  
  availability_zones = ["ap-southeast-3a"]
  
  flavor            = var.redis_instance_type
  maintain_begin    = "02:00:00"  # Maintenance window start
  maintain_end      = "06:00:00"  # Maintenance window end
  password          = var.redis_password
  
  # Add whitelist for app subnet CIDR
  whitelist_enable = true
  whitelists {
    group_name = "app-tier"
    ip_address = ["10.0.2.0/24"]  # App subnet CIDR - replace with actual value or variable
  }
  
  backup_policy {
    backup_type = "auto"
    begin_at    = "00:00-01:00"
    period_type = "weekly"
    backup_at   = [1] # Monday
    save_days   = 7
  }
  
  tags = {
    Name        = "${var.project_name}-redis"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Update PostgreSQL credentials with actual endpoint
resource "huaweicloud_csms_secret" "postgres_credentials_update" {
  name        = "${var.project_name}-postgres-credentials"
  description = "PostgreSQL database credentials"
  
  # Update with actual PostgreSQL endpoint after creation
  secret_text = jsonencode({
    username  = var.postgres_username
    password  = var.postgres_password
    host      = huaweicloud_rds_instance.postgres.private_ips[0]
    port      = 5432
    database  = var.postgres_db_name
  })
  
  kms_key_id  = var.kms_key_id
  
  # Ensure the database exists before updating
  depends_on = [huaweicloud_rds_instance.postgres, huaweicloud_rds_database.app_database]
}