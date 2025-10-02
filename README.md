# PredKit Backend

AI-powered serverless backend with PostgreSQL database on Hetzner VPS.

## Stack

- **Database**: PostgreSQL 17 with pgai, pg_search, vector extensions
- **Infrastructure**: Terraform (GCP Registry + Hetzner VPS)
- **Config**: Ansible for automated server setup
- **Functions**: Python with uv (ready for GCP Cloud Functions)

## Structure

```
backend/
├── api/                # Cloud Functions (HTTP endpoints)
├── indexers/           # Background processing functions
├── terraform/          # Infrastructure as Code
├── ansible/            # Server configuration
└── shared/             # Shared Python modules
```

## Local Development

```bash
# 1. Authenticate with GCP (one-time)
gcloud auth configure-docker europe-west3-docker.pkg.dev

# 2. Create env file
cp env.example .env
# Edit .env with your local settings

# 3. Start database
docker compose -f .dev/compose.yml --env-file .env up -d

# 4. Run migrations
uv run alembic upgrade head

# 5. Connect to DB (optional)
docker exec -it predkit-db psql -U pikachu -d predkit
```

## Production Deployment

1. **Deploy Infrastructure & Database:**
   ```bash
   # Configure secrets
   cp terraform/terraform.tfvars.example terraform/terraform.tfvars
   
   # Deploy infrastructure
   cd deploy/terraform && terraform apply
   
   # Configure server + WireGuard VPN
   cd ../ansible && ./run.sh
   ```

2. **Setup VPN Client:**
   ```bash
   # Client configs will be downloaded to deploy/ansible/wireguard-clients/
   sudo cp deploy/ansible/wireguard-clients/local-dev.conf /etc/wireguard/predkit.conf
   sudo wg-quick up predkit
   
   # Verify VPN connection
   ping 10.0.100.1
   ```
   
   See [deploy/ansible/WIREGUARD_SETUP.md](deploy/ansible/WIREGUARD_SETUP.md) for detailed instructions.

3. **Update Connection Strings:**
   ```bash
   # Update .env to use VPN IP
   DB_HOST=10.0.100.1  # Instead of public IP
   ```

4. **Access Database:**
   ```bash
   # Via VPN
   psql "postgresql://pikachu:password@10.0.100.1:5432/predkit"
   
   # Or SSH to server
   ssh root@<server-ip> 'docker exec -it predkit-db psql -U pikachu -d predkit'
   ```

## Extensions

- **pgai**: AI/ML workflows and vectorization
- **pg_search**: Full-text search with BM25
- **vector**: Embedding storage and similarity search
