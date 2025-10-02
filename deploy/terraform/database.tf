# Hetzner VPS for PostgreSQL Database
resource "hcloud_server" "database" {
  name        = "db"
  image       = "ubuntu-24.04"
  server_type = "cpx21"  # 3 vCPU (AMD, Shared), 4GB RAM, 80GB SSD
  location    = local.hetzner_location
  
  ssh_keys = [data.hcloud_ssh_key.deploy.id]
  
  # Request both IPv4 and IPv6 addresses
  public_net {
    ipv4_enabled = true
    ipv6_enabled = true
  }

  labels = {
    service = "database"
    project = "PredKit"
  }
}

# Use existing SSH key
data "hcloud_ssh_key" "deploy" {
  name = "dali-ubuntu"
}

# Firewall for database server
resource "hcloud_firewall" "database" {
  name = "db-firewall"

  # SSH access
  rule {
    direction = "in"
    port      = "22"
    protocol  = "tcp"
    source_ips = ["0.0.0.0/0"]
  }

  # WireGuard VPN
  rule {
    direction = "in"
    port      = "51820"
    protocol  = "udp"
    source_ips = ["0.0.0.0/0"]
  }

  # PostgreSQL access is now restricted to WireGuard VPN network (10.0.100.0/24)
  # The database will only bind to the WireGuard interface
}

resource "hcloud_firewall_attachment" "database" {
  firewall_id = hcloud_firewall.database.id
  server_ids  = [hcloud_server.database.id]
}

# Output database connection info
output "database_ip" {
  value = hcloud_server.database.ipv4_address
}
