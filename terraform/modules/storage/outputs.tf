output "logs_bucket" {
  description = "The logs bucket details"
  value = {
    name = huaweicloud_obs_bucket.logs.bucket
    id   = huaweicloud_obs_bucket.logs.id
    url  = "https://${huaweicloud_obs_bucket.logs.bucket}.obs.${var.region}.myhuaweicloud.com"
  }
}

output "artifacts_bucket" {
  description = "The application artifacts bucket details"
  value = {
    name = huaweicloud_obs_bucket.artifacts.bucket
    id   = huaweicloud_obs_bucket.artifacts.id
    url  = "https://${huaweicloud_obs_bucket.artifacts.bucket}.obs.${var.region}.myhuaweicloud.com"
  }
}

output "static_assets_bucket" {
  description = "The static assets bucket details"
  value = {
    name = huaweicloud_obs_bucket.static_assets.bucket
    id   = huaweicloud_obs_bucket.static_assets.id
    url  = "https://${huaweicloud_obs_bucket.static_assets.bucket}.obs.${var.region}.myhuaweicloud.com"
    website_url = "https://${huaweicloud_obs_bucket.static_assets.bucket}.obs-website.${var.region}.myhuaweicloud.com"
  }
}

output "backups_bucket" {
  description = "The backups bucket details"
  value = {
    name = huaweicloud_obs_bucket.backups.bucket
    id   = huaweicloud_obs_bucket.backups.id
    url  = "https://${huaweicloud_obs_bucket.backups.bucket}.obs.${var.region}.myhuaweicloud.com"
  }
}