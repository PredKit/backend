# Deployment Guide

Complete guide for deploying PredKit backend infrastructure.

## Prerequisites

- Google Cloud Platform account with billing enabled
- Hetzner Cloud account
- Terraform installed locally
- Ansible installed locally
- Docker installed locally

## Initial Setup

### 1. Setup GCP

```bash
cd deploy/scripts
./setup-gcp.sh
```

This enables required APIs and creates the Artifact Registry.

### 2. Deploy Infrastructure

```bash
cd deploy/scripts
./deploy-db.sh
```

This creates:
- Hetzner VPS server
- GCP Artifact Registry
- Firewall rules (SSH, WireGuard VPN)

### 3. Configure Server & Deploy Database

```bash
cd deploy/ansible
./run.sh
```

This:
- Installs Docker and GCP SDK
- Sets up WireGuard VPN
- Deploys PostgreSQL container
- Creates systemd timer for indexer
- Downloads VPN client configs to `wireguard-clients/`

## Database Access

### Via VPN (Secure - Recommended)

1. Install WireGuard:
   ```bash
   # Linux
   sudo apt install wireguard
   
   # macOS
   brew install wireguard-tools
   ```

2. Setup VPN:
   ```bash
   sudo cp deploy/ansible/wireguard-clients/local-dev.conf /etc/wireguard/predkit.conf
   sudo chmod 600 /etc/wireguard/predkit.conf
   sudo wg-quick up predkit
   ```

3. Test connection:
   ```bash
   ping 10.0.100.1
   psql "postgresql://pikachu:password@10.0.100.1:5432/predkit"
   ```

### Via SSH (Alternative)

```bash
ssh root@<server-ip> 'docker exec -it predkit-db psql -U pikachu -d predkit'
```

## Indexer Deployment

The indexer runs on the DB server, triggered hourly by systemd.

### Deploy New Indexer Version

```bash
# 1. Build and push image
cd deploy/scripts
./deploy-indexer.sh

# 2. Pull on server
ssh root@<server-ip> 'cd /opt/predkit && docker compose pull indexer'

# Optional: Trigger immediately
ssh root@<server-ip> 'systemctl start indexer.service'
```

## API Deployment

The API runs on the same server, behind nginx reverse proxy.

### Deploy New API Version

```bash
# 1. Build and push image
cd deploy/scripts
./deploy-api.sh

# 2. Deploy to server (pulls image, restarts API, reloads nginx)
cd ../ansible
./run.sh
```

### Access API

- **HTTPS**: `https://api.predkit.com/`
- **Swagger docs**: `https://api.predkit.com/docs`
- **Health check**: `https://api.predkit.com/health`

### Setup Custom Domain & SSL

1. **Point your domain** to the server IP (A record)

2. **Update secrets file** (already configured):
   ```yaml
   # deploy/ansible/vars/secrets.yml
   api_domain_name: "api.predkit.com"
   letsencrypt_email: "mohamedalichelbi123@gmail.com"
   ```

3. **Re-run Ansible** (it will automatically obtain SSL certificate):
   ```bash
   cd deploy/ansible && ./run.sh
   ```

Ansible will:
- Install certbot
- Obtain Let's Encrypt SSL certificate
- Configure nginx for HTTPS
- Enable certbot.timer (automatic renewal twice daily)
- Set up nginx reload hook on certificate renewal

**Note**: 
- HTTP requests are automatically redirected to HTTPS
- Certificates auto-renew before expiration (systemd timer)
- Nginx automatically reloads when certificates are renewed

### Monitor Indexer

```bash
# Check timer status
ssh root@<server-ip> 'systemctl status indexer.timer'

# View logs
ssh root@<server-ip> 'journalctl -u indexer.service -f'

# List recent runs
ssh root@<server-ip> 'journalctl -u indexer.service -n 50'
```

## VPN Client Management

### Available Clients

- `local-dev` (10.0.100.2) - Your development machine
- `admin-laptop` (10.0.100.3) - Administrative access
- `ci-cd` (10.0.100.4) - CI/CD pipelines
- `api` (10.0.100.11) - Future API server

### Add New Client

1. Edit `deploy/ansible/setup-database.yml`:
   ```yaml
   wireguard_clients:
     # ... existing ...
     - name: "new-client"
       vpn_ip: "10.0.100.12"
       persistent_keepalive: true
   ```

2. Regenerate:
   ```bash
   cd deploy/ansible && ./run.sh
   ```

3. Config will be at: `wireguard-clients/new-client.conf`

## Database Migrations

```bash
# Make sure VPN is connected
sudo wg show

# Run migrations
uv run alembic upgrade head
```

## Troubleshooting

### Can't connect to database

1. Check VPN is active: `sudo wg show`
2. Ping server: `ping 10.0.100.1`
3. Test port: `nc -zv 10.0.100.1 5432`

### Indexer not running

1. Check timer: `ssh root@<server-ip> 'systemctl status indexer.timer'`
2. Check service: `ssh root@<server-ip> 'systemctl status indexer.service'`
3. View logs: `ssh root@<server-ip> 'journalctl -u indexer.service -n 100'`

### API not responding

1. Check nginx: `ssh root@<server-ip> 'systemctl status nginx'`
2. Check API container: `ssh root@<server-ip> 'docker ps | grep predkit-api'`
3. Check API logs: `ssh root@<server-ip> 'docker logs predkit-api -f'`
4. Check nginx logs: `ssh root@<server-ip> 'tail -f /var/log/nginx/predkit-api-error.log'`
5. Test localhost: `ssh root@<server-ip> 'curl http://localhost:8000/health'`

### Regenerate VPN keys

If keys are compromised:

```bash
# SSH to server and delete old keys
ssh root@<server-ip> 'rm /etc/wireguard/client_* /etc/wireguard/server_*'

# Re-run Ansible
cd deploy/ansible && ./run.sh

# Redistribute new configs to team
```

