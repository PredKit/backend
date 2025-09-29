# Scripts

Collection of utility scripts for PredKit backend deployment and management.

## Available Scripts

### `setup-gcp.sh`
Sets up Google Cloud Platform prerequisites.
```bash
./scripts/setup-gcp.sh
```

### `deploy.sh` 
Deploys the database infrastructure to Hetzner + GCP.
```bash
./scripts/deploy.sh [environment]
# Example: ./scripts/deploy.sh dev
```

## Usage

All scripts should be run from the project root directory:
```bash
cd /path/to/predkit/backend
./scripts/script-name.sh
```
