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

## Quick Start

1. **Deploy Database:**
   ```bash
   # Configure secrets
   cp terraform/terraform.tfvars.example terraform/terraform.tfvars
   
   # Deploy infrastructure
   cd terraform && terraform apply
   
   # Configure server
   cd ../ansible && ./run.sh
   ```

2. **Access Database:**
   ```bash
   ssh root@<server-ip> 'docker exec -it predkit-db psql -U pikachu -d predkit'
   ```

## Extensions

- **pgai**: AI/ML workflows and vectorization
- **pg_search**: Full-text search with BM25
- **vector**: Embedding storage and similarity search
