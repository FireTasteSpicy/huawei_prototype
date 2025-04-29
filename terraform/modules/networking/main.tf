#-------------------------------------
# VPC Resource
#-------------------------------------
resource "huaweicloud_vpc" "main" {
  name = var.vpc_name
  cidr = var.vpc_cidr
  
  tags = {
    Name        = var.vpc_name
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

#-------------------------------------
# Subnet Resources
#-------------------------------------
# Web tier subnet (public)
resource "huaweicloud_vpc_subnet" "web" {
  name       = "${var.vpc_name}-web-subnet"
  cidr       = var.web_subnet_cidr
  gateway_ip = cidrhost(var.web_subnet_cidr, 1)
  vpc_id     = huaweicloud_vpc.main.id
  
  tags = {
    Name  = "${var.vpc_name}-web-subnet"
    Tier  = "web"
  }
}

# Application tier subnet (private)
resource "huaweicloud_vpc_subnet" "app" {
  name       = "${var.vpc_name}-app-subnet"
  cidr       = var.app_subnet_cidr
  gateway_ip = cidrhost(var.app_subnet_cidr, 1)
  vpc_id     = huaweicloud_vpc.main.id
  
  tags = {
    Name  = "${var.vpc_name}-app-subnet"
    Tier  = "application"
  }
}

# Database tier subnet (private)
resource "huaweicloud_vpc_subnet" "db" {
  name       = "${var.vpc_name}-db-subnet"
  cidr       = var.db_subnet_cidr
  gateway_ip = cidrhost(var.db_subnet_cidr, 1)
  vpc_id     = huaweicloud_vpc.main.id
  
  tags = {
    Name  = "${var.vpc_name}-db-subnet"
    Tier  = "database"
  }
}

# Management subnet
resource "huaweicloud_vpc_subnet" "management" {
  name       = "${var.vpc_name}-mgmt-subnet"
  cidr       = var.management_subnet_cidr
  gateway_ip = cidrhost(var.management_subnet_cidr, 1)
  vpc_id     = huaweicloud_vpc.main.id
  
  tags = {
    Name  = "${var.vpc_name}-mgmt-subnet"
    Tier  = "management"
  }
}

#-------------------------------------
# Security Groups
#-------------------------------------
# Web tier security group
resource "huaweicloud_networking_secgroup" "web" {
  name        = "web-sg"
  description = "Security group for web tier"
}

# Allow HTTP and HTTPS from anywhere
resource "huaweicloud_networking_secgroup_rule" "web_http" {
  security_group_id = huaweicloud_networking_secgroup.web.id
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 80
  port_range_max    = 80
  remote_ip_prefix  = "0.0.0.0/0"
}

resource "huaweicloud_networking_secgroup_rule" "web_https" {
  security_group_id = huaweicloud_networking_secgroup.web.id
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 443
  port_range_max    = 443
  remote_ip_prefix  = "0.0.0.0/0"
}

# App tier security group
resource "huaweicloud_networking_secgroup" "app" {
  name        = "app-sg"
  description = "Security group for application tier"
}

# Allow traffic from web tier to app tier on Django port
resource "huaweicloud_networking_secgroup_rule" "app_from_web" {
  security_group_id = huaweicloud_networking_secgroup.app.id
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 8000
  port_range_max    = 8000
  remote_group_id   = huaweicloud_networking_secgroup.web.id
}

# Database tier security group
resource "huaweicloud_networking_secgroup" "db" {
  name        = "db-sg"
  description = "Security group for database tier"
}

# Allow traffic from app tier to db tier on PostgreSQL port
resource "huaweicloud_networking_secgroup_rule" "db_from_app" {
  security_group_id = huaweicloud_networking_secgroup.db.id
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 5432
  port_range_max    = 5432
  remote_group_id   = huaweicloud_networking_secgroup.app.id
}

# Management security group
resource "huaweicloud_networking_secgroup" "management" {
  name        = "management-sg"
  description = "Security group for management access"
}

# Allow SSH from admin IPs
resource "huaweicloud_networking_secgroup_rule" "ssh_access" {
  count             = length(var.admin_ip_addresses)
  security_group_id = huaweicloud_networking_secgroup.management.id
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = var.admin_ip_addresses[count.index]
}

# Allow all outbound traffic for all security groups
resource "huaweicloud_networking_secgroup_rule" "web_outbound" {
  security_group_id = huaweicloud_networking_secgroup.web.id
  direction         = "egress"
  ethertype         = "IPv4"
  remote_ip_prefix  = "0.0.0.0/0"
}

resource "huaweicloud_networking_secgroup_rule" "app_outbound" {
  security_group_id = huaweicloud_networking_secgroup.app.id
  direction         = "egress"
  ethertype         = "IPv4"
  remote_ip_prefix  = "0.0.0.0/0"
}

resource "huaweicloud_networking_secgroup_rule" "db_outbound" {
  security_group_id = huaweicloud_networking_secgroup.db.id
  direction         = "egress"
  ethertype         = "IPv4"
  remote_ip_prefix  = "0.0.0.0/0"
}

resource "huaweicloud_networking_secgroup_rule" "mgmt_outbound" {
  security_group_id = huaweicloud_networking_secgroup.management.id
  direction         = "egress"
  ethertype         = "IPv4"
  remote_ip_prefix  = "0.0.0.0/0"
}

#-------------------------------------
# NAT Gateway for Outbound Internet Access
#-------------------------------------
# Elastic IP for NAT Gateway
resource "huaweicloud_vpc_eip" "nat_gateway" {
  publicip {
    type = "5_bgp"
  }
  bandwidth {
    name        = "nat-bandwidth"
    size        = 5
    share_type  = "PER"
    charge_mode = "traffic"
  }
}

# NAT Gateway
resource "huaweicloud_nat_gateway" "main" {
  name                = "${var.vpc_name}-nat-gateway"
  spec                = "1"  # Small specification
  vpc_id              = huaweicloud_vpc.main.id
  subnet_id           = huaweicloud_vpc_subnet.web.id
}

# SNAT Rule (for private subnets to access internet)
resource "huaweicloud_nat_snat_rule" "app_tier" {
  nat_gateway_id = huaweicloud_nat_gateway.main.id
  subnet_id      = huaweicloud_vpc_subnet.app.id
  floating_ip_id = huaweicloud_vpc_eip.nat_gateway.id
}

resource "huaweicloud_nat_snat_rule" "db_tier" {
  nat_gateway_id = huaweicloud_nat_gateway.main.id
  subnet_id      = huaweicloud_vpc_subnet.db.id
  floating_ip_id = huaweicloud_vpc_eip.nat_gateway.id
}