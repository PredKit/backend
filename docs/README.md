# PredKit Backend Documentation

## Quick Links

- **[Architecture](./ARCHITECTURE.md)** - System design, infrastructure, and technology stack
- **[Deployment Guide](./DEPLOYMENT.md)** - Complete deployment instructions and troubleshooting

## Project Overview

PredKit is an AI-powered prediction market aggregator with a PostgreSQL database hosted on Hetzner VPS. The indexer runs hourly to collect events from various prediction market platforms (Kalshi, Polymarket).

## Key Features

- **Secure Database Access**: All connections via WireGuard VPN
- **Cost-Effective**: ~€5/month infrastructure costs
- **Co-located Processing**: Indexer runs on same server as database for zero latency
- **PostgreSQL Extensions**: pgai (AI/ML), pg_search (full-text), vector (embeddings)
- **Infrastructure as Code**: Terraform + Ansible

## Documentation Structure

```
docs/
├── README.md           # This file
├── ARCHITECTURE.md     # System design and architecture
├── DEPLOYMENT.md       # Deployment guide and operations
├── scripts/
│   └── README.md       # Deployment scripts reference
└── vpn/
    └── README.md       # VPN client configs
```

## Quick Start

See the main [README.md](../README.md) for local development setup.

For production deployment, follow [DEPLOYMENT.md](./DEPLOYMENT.md).

## Getting Help

- **Architecture questions**: See [ARCHITECTURE.md](./ARCHITECTURE.md)
- **Deployment issues**: See [DEPLOYMENT.md](./DEPLOYMENT.md) troubleshooting section
- **Deployment scripts**: See [scripts/README.md](./scripts/README.md)
- **VPN setup**: See [vpn/README.md](./vpn/README.md)

