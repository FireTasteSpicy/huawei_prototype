# KMS Key for encrypting secrets
resource "huaweicloud_kms_key" "secrets_key" {
  key_alias       = "${var.project_name}-${var.kms_key_alias}"
  key_description = "KMS key for encrypting application secrets"
  pending_days    = 7     # Pending days before key is deleted
  is_enabled      = true
  
  tags = {
    Name        = "${var.project_name}-kms-key"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Generate a strong random password for PostgreSQL master user
resource "random_password" "postgres_password" {
  length           = 16
  special          = true
  override_special = "!"
  min_upper        = 2
  min_lower        = 2
  min_numeric      = 2
  min_special      = 2
}

# Generate a strong random password for Redis
resource "random_password" "redis_password" {
  length           = 16
  special          = true
  override_special = "!"
  min_upper        = 2
  min_lower        = 2
  min_numeric      = 2
  min_special      = 2
}

# Create a CSMS (Cloud Secret Management Service) for storing secrets
resource "huaweicloud_csms_secret" "postgres_credentials" {
  name        = "${var.project_name}-postgres-credentials"
  description = "PostgreSQL database credentials"
  
  # Store credentials in JSON format
  secret_text = jsonencode({
    username  = "postgres_admin"
    password  = random_password.postgres_password.result
    host      = "to_be_updated_after_db_creation" # Will be updated later
    port      = 5432
    database  = "${var.project_name}_db"
  })
  
  kms_key_id = huaweicloud_kms_key.secrets_key.id
}

resource "huaweicloud_csms_secret" "redis_credentials" {
  name        = "${var.project_name}-redis-credentials"
  description = "Redis cache credentials"
  
  # Store credentials in JSON format
  secret_text = jsonencode({
    password  = random_password.redis_password.result
    host      = "to_be_updated_after_redis_creation" # Will be updated later
    port      = 6379
  })
  
  kms_key_id = huaweicloud_kms_key.secrets_key.id
}