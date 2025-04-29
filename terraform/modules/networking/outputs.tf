output "vpc_id" {
  description = "ID of the created VPC"
  value       = huaweicloud_vpc.main.id
}

output "web_subnet_id" {
  description = "ID of the web subnet"
  value       = huaweicloud_vpc_subnet.web.id
}

output "app_subnet_id" {
  description = "ID of the app subnet"
  value       = huaweicloud_vpc_subnet.app.id
}

output "db_subnet_id" {
  description = "ID of the db subnet"
  value       = huaweicloud_vpc_subnet.db.id
}

output "management_subnet_id" {
  description = "ID of the management subnet"
  value       = huaweicloud_vpc_subnet.management.id
}

output "web_security_group_id" {
  description = "ID of the web security group"
  value       = huaweicloud_networking_secgroup.web.id
}

output "app_security_group_id" {
  description = "ID of the application security group"
  value       = huaweicloud_networking_secgroup.app.id
}

output "db_security_group_id" {
  description = "ID of the database security group"
  value       = huaweicloud_networking_secgroup.db.id
}

output "management_security_group_id" {
  description = "ID of the management security group"
  value       = huaweicloud_networking_secgroup.management.id
}

output "nat_gateway_id" {
  description = "ID of the NAT Gateway"
  value       = huaweicloud_nat_gateway.main.id
}

output "nat_gateway_eip" {
  description = "Public IP address of the NAT Gateway"
  value       = huaweicloud_vpc_eip.nat_gateway.address
}