# Deployment Steps - WireGuard VPN Update

## Overview

This update secures your PostgreSQL database by putting it behind a WireGuard VPN. The database will no longer be exposed on the public internet.

## Prerequisites

- Existing Hetzner VPS running PostgreSQL
- SSH access to the server
- Terraform installed locally
- Ansible installed locally

## Step 1: Update Terraform (Optional but Recommended)

The Terraform configuration has been updated to:
- Remove public PostgreSQL access (port 5432)
- Add WireGuard VPN access (port 51820/UDP)

```bash
cd deploy/terraform
terraform plan
terraform apply
```

**Note**: If you skip this step, the firewall will still allow PostgreSQL on port 5432 temporarily, but the database will only bind to the WireGuard interface after Ansible runs.

## Step 2: Deploy WireGuard with Ansible

Run the Ansible playbook to:
- Install and configure WireGuard
- Generate server and client keys
- Update PostgreSQL to only listen on the VPN interface
- Download client configurations

```bash
cd deploy/ansible
./run.sh
```

The playbook will:
1. Install WireGuard on the server
2. Generate cryptographic keys
3. Configure the VPN network (10.0.100.0/24)
4. Reconfigure PostgreSQL to bind to 10.0.100.1
5. Download client configs to `wireguard-clients/`

## Step 3: Setup Client VPN

After the playbook completes, client configurations will be available in:
```
deploy/ansible/wireguard-clients/
├── local-dev.conf
├── admin-laptop.conf
└── ci-cd.conf
```

### Linux/macOS Setup

```bash
# Install WireGuard
sudo apt install wireguard  # Debian/Ubuntu
brew install wireguard-tools  # macOS

# Copy configuration
sudo cp deploy/ansible/wireguard-clients/local-dev.conf /etc/wireguard/predkit.conf
sudo chmod 600 /etc/wireguard/predkit.conf

# Start VPN
sudo wg-quick up predkit

# Verify connection
ping 10.0.100.1
```

## Step 4: Update Connection Strings

Update all database connection strings to use the VPN IP:

### Environment Variables

Update your `.env` files:
```bash
# Before
DB_HOST=<public-server-ip>

# After
DB_HOST=10.0.100.1
```

### Connection Strings

```bash
# Before
postgresql://user:pass@<public-ip>:5432/predkit

# After
postgresql://user:pass@10.0.100.1:5432/predkit
```

### Alembic Configuration

The `alembic.ini` and `src/shared/config.py` will automatically pick up the new `DB_HOST` from environment variables.

## Step 5: Test Connection

1. Connect to VPN:
   ```bash
   sudo wg-quick up predkit
   ```

2. Test database access:
   ```bash
   psql "postgresql://pikachu:password@10.0.100.1:5432/predkit"
   ```

3. Run migrations (if needed):
   ```bash
   uv run alembic upgrade head
   ```

4. Test your application:
   ```bash
   # Make sure VPN is active
   sudo wg show
   
   # Run your app
   uv run python src/indexers/main.py
   ```

## Adding New Clients

To add a new client (e.g., for a team member or CI/CD):

1. Edit `deploy/ansible/setup-database.yml`:
   ```yaml
   wireguard_clients:
     # ... existing clients ...
     - name: "new-client-name"
       vpn_ip: "10.0.100.5"  # Pick next available IP
       persistent_keepalive: true
   ```

2. Re-run Ansible:
   ```bash
   cd deploy/ansible && ./run.sh
   ```

3. Share the generated config:
   ```bash
   # Config will be at:
   deploy/ansible/wireguard-clients/new-client-name.conf
   ```

## Troubleshooting

### Can't connect to VPN

1. Check firewall allows UDP 51820:
   ```bash
   nc -zvu <server-ip> 51820
   ```

2. Check WireGuard is running on server:
   ```bash
   ssh root@<server-ip>
   systemctl status wg-quick@wg0
   sudo wg show
   ```

### Can't connect to database

1. Verify VPN is active:
   ```bash
   sudo wg show
   ping 10.0.100.1
   ```

2. Test PostgreSQL port:
   ```bash
   nc -zv 10.0.100.1 5432
   ```

3. Check PostgreSQL logs:
   ```bash
   ssh root@<server-ip>
   docker logs predkit-db
   ```

### Database connection refused

Make sure you:
1. Have the VPN connected: `sudo wg show`
2. Updated DB_HOST to `10.0.100.1`
3. Can ping the VPN server: `ping 10.0.100.1`

