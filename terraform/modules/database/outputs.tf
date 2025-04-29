output "rds_instance_id" {
  description = "ID of the PostgreSQL RDS instance"
  value       = huaweicloud_rds_instance.postgres.id
}

output "rds_instance_endpoint" {
  description = "Connection endpoint of the PostgreSQL RDS instance"
  value       = huaweicloud_rds_instance.postgres.private_ips[0]
}

output "rds_instance_port" {
  description = "Port of the PostgreSQL RDS instance"
  value       = 5432
}

output "postgres_db_name" {
  description = "Name of the PostgreSQL database"
  value       = var.postgres_db_name
}

output "redis_instance_id" {
  description = "ID of the Redis instance"
  value       = huaweicloud_dcs_instance.redis.id
}

output "redis_instance_ip" {
  description = "Private IP of the Redis instance"
  value       = huaweicloud_dcs_instance.redis.private_ip
}

output "redis_instance_port" {
  description = "Port of the Redis instance"
  value       = huaweicloud_dcs_instance.redis.port
}

output "redis_connection_info" {
  description = "Redis connection information"
  value = {
    host     = huaweicloud_dcs_instance.redis.ip
    port     = huaweicloud_dcs_instance.redis.port
    password = var.redis_password  # Note: exposing this in outputs is not secure for production
  }
  sensitive = true
}