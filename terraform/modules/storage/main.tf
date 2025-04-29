locals {
  timestamp = formatdate("YYMMDDhhmmss", timestamp())
  
  # Generate bucket names with project prefix if not provided
  logs_bucket_name = var.logs_bucket_name != null ? var.logs_bucket_name : "${var.project_name}-logs-${local.timestamp}"
  artifacts_bucket_name = var.artifacts_bucket_name != null ? var.artifacts_bucket_name : "${var.project_name}-artifacts-${local.timestamp}"
  static_assets_bucket_name = var.static_assets_bucket_name != null ? var.static_assets_bucket_name : "${var.project_name}-static-${local.timestamp}"
  backups_bucket_name = var.backups_bucket_name != null ? var.backups_bucket_name : "${var.project_name}-backups-${local.timestamp}"
}

# Logs Bucket
resource "huaweicloud_obs_bucket" "logs" {
  bucket        = local.logs_bucket_name
  storage_class = "STANDARD"
  acl           = "log-delivery-write"  # Use this ACL instead of grant blocks
  force_destroy = true
  
  versioning = true
  
  # Fix the lifecycle rule by adding a name
    lifecycle_rule {
        name     = "log-rotation"
        prefix   = ""  # Empty prefix to apply to all objects
        enabled  = true
        expiration {
            days = 90
        }
    }

  tags = {
    Name        = "${var.project_name}-logs"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Application Artifacts Bucket
resource "huaweicloud_obs_bucket" "artifacts" {
  bucket        = local.artifacts_bucket_name
  storage_class = "STANDARD"
  acl           = "private"
  force_destroy = true
  
  versioning = true

  logging {
    target_bucket = huaweicloud_obs_bucket.logs.bucket
    target_prefix = "artifacts-logs/"
  }

  tags = {
    Name        = "${var.project_name}-artifacts"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Static Website Assets Bucket
resource "huaweicloud_obs_bucket" "static_assets" {
  bucket        = local.static_assets_bucket_name
  storage_class = "STANDARD"
  acl           = "public-read" # For website static assets
  force_destroy = true
  
  website {
    index_document = "index.html"
    error_document = "error.html"
  }

  cors_rule {
    allowed_origins = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_headers = ["*"]
    max_age_seconds = 3000
  }

  logging {
    target_bucket = huaweicloud_obs_bucket.logs.bucket
    target_prefix = "static-assets-logs/"
  }

  tags = {
    Name        = "${var.project_name}-static-assets"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Backups Bucket
resource "huaweicloud_obs_bucket" "backups" {
  bucket        = local.backups_bucket_name
  storage_class = "WARM" # Use WARM for backups to reduce costs
  acl           = "private"
  force_destroy = true
  
  versioning = true

  lifecycle_rule {
    name    = "backup-retention"
    enabled = true
    
    expiration {
      days = 365 # Keep backups for 1 year
    }
    
    transition {
      days          = 90
      storage_class = "COLD" # Move to cold storage after 90 days
    }
  }

  logging {
    target_bucket = huaweicloud_obs_bucket.logs.bucket
    target_prefix = "backups-logs/"
  }

  tags = {
    Name        = "${var.project_name}-backups"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}