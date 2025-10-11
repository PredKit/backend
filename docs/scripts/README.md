# Deployment Scripts

Collection of deployment scripts for PredKit backend.

## Available Scripts

### `setup-gcp.sh`
Initial GCP setup - enables APIs and creates Artifact Registry.
```bash
cd deploy/scripts
./setup-gcp.sh
```

### `deploy-db.sh`
Deploys database infrastructure (Hetzner VPS + GCP resources) via Terraform.
```bash
cd deploy/scripts
./deploy-db.sh
```

### `deploy-indexer.sh`
Builds and pushes indexer Docker image to GCP Artifact Registry.
```bash
cd deploy/scripts
./deploy-indexer.sh
```

## Full Deployment Flow

See [../DEPLOYMENT.md](../DEPLOYMENT.md) for complete deployment guide.
