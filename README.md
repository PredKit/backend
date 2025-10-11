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
├── src/
│   ├── api/                    # Cloud Functions (HTTP endpoints)
│   ├── indexers/               # Background processing
│   │   ├── kalshi/            # Kalshi market collector
│   │   ├── polymarket/        # Polymarket collector
│   │   ├── indexer.py         # Main indexing logic
│   │   └── run.py             # Production entrypoint
│   └── shared/                # Shared Python modules
├── deploy/
│   ├── terraform/             # Infrastructure as Code
│   └── ansible/               # Server configuration & indexer deployment
├── alembic/                   # Database migrations
├── Dockerfile.indexer         # Indexer container image
└── test_indexer.py            # Local testing script
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

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for complete deployment guide.

**Quick Start:**

1. **Deploy Infrastructure:**
   ```bash
   cd deploy/scripts
   ./setup-gcp.sh    # One-time GCP setup
   ./deploy-db.sh    # Deploy Hetzner VPS + GCP registry
   ```

2. **Configure Server:**
   ```bash
   cd ../ansible
   ./run.sh          # Setup Docker, WireGuard, PostgreSQL
   ```

3. **Setup VPN & Connect:**
   ```bash
   sudo cp deploy/ansible/wireguard-clients/local-dev.conf /etc/wireguard/predkit.conf
   sudo wg-quick up predkit
   ping 10.0.100.1
   psql "postgresql://pikachu:password@10.0.100.1:5432/predkit"
   ```

## Indexer Deployment

The indexer runs hourly on the DB server via systemd timer.

```bash
cd deploy/scripts
./deploy-indexer.sh  # Build & push image
```

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for monitoring and troubleshooting.

## Extensions

- **pgai**: AI/ML workflows and vectorization
- **pg_search**: Full-text search with BM25
- **vector**: Embedding storage and similarity search
