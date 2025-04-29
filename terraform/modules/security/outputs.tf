output "kms_key_id" {
  description = "The ID of the KMS key used for encryption"
  value       = huaweicloud_kms_key.secrets_key.id
}

output "postgres_password" {
  description = "The generated PostgreSQL password (only for initial setup)"
  value       = random_password.postgres_password.result
  sensitive   = true
}

output "redis_password" {
  description = "The generated Redis password (only for initial setup)"
  value       = random_password.redis_password.result
  sensitive   = true
}

output "postgres_secret_name" {
  description = "The name of the secret containing PostgreSQL credentials"
  value       = huaweicloud_csms_secret.postgres_credentials.name
}

output "redis_secret_name" {
  description = "The name of the secret containing Redis credentials"
  value       = huaweicloud_csms_secret.redis_credentials.name
}