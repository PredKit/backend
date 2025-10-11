# Architecture

## Overview

PredKit backend is a serverless AI-powered prediction market aggregator with a PostgreSQL database hosted on Hetzner VPS.

## Infrastructure

### Hosting

- **Database**: Hetzner VPS (€4.15/month)
  - Location: Germany
  - PostgreSQL 17 with extensions (pgai, pg_search, vector)
  - Docker Compose for container management
  
- **Container Registry**: GCP Artifact Registry
  - Stores DB and indexer images
  - Region: europe-west3 (Frankfurt)

- **Indexer**: Runs on same VPS as database
  - Systemd timer (hourly execution)
  - Docker container
  - Direct localhost access to DB

### Network Security

- **WireGuard VPN**: All database access via encrypted VPN
  - VPN Network: 10.0.100.0/24
  - Server: 10.0.100.1
  - No public database port exposed
  - Firewall: Only SSH (22) and WireGuard (51820/UDP)

### Components

```
┌─────────────────────────────────────────────────┐
│          Hetzner VPS (88.99.86.51)             │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │        WireGuard VPN (10.0.100.1)       │  │
│  │                                          │  │
│  │  ┌────────────────┐  ┌───────────────┐  │  │
│  │  │ PostgreSQL 17  │  │   Indexer     │  │  │
│  │  │  (port 5432)   │◄─┤ (systemd job) │  │  │
│  │  │                │  │               │  │  │
│  │  │ • pgai         │  └───────────────┘  │  │
│  │  │ • pg_search    │                     │  │
│  │  │ • vector       │                     │  │
│  │  └────────────────┘                     │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│  Public Ports:                                  │
│  • 22 (SSH)                                     │
│  • 51820/UDP (WireGuard)                        │
└─────────────────────────────────────────────────┘
          ▲
          │ VPN Tunnel
          │
┌─────────┴────────────────────────────────────┐
│    VPN Clients (10.0.100.x)                  │
│                                              │
│  • Local Dev    (10.0.100.2)                │
│  • Admin Laptop (10.0.100.3)                │
│  • CI/CD        (10.0.100.4)                │
│  • Future API   (10.0.100.11)               │
└──────────────────────────────────────────────┘
```

## Data Flow

### Indexer (Hourly)

```
Timer triggers (hourly)
  ↓
Systemd starts indexer service
  ↓
Docker Compose runs container
  ↓
Python script fetches events from:
  • Kalshi API
  • Polymarket API
  ↓
Stores/updates in PostgreSQL (localhost)
  ↓
Container exits, removed (--rm)
```

### Database Access

```
Developer Machine
  ↓
WireGuard VPN (encrypted)
  ↓
Server VPN interface (10.0.100.1)
  ↓
PostgreSQL container (bound to VPN IP)
```

## Technology Stack

### Infrastructure
- **IaC**: Terraform (GCP + Hetzner Cloud)
- **Configuration**: Ansible (server setup, WireGuard, Docker)
- **Containers**: Docker + Docker Compose
- **Orchestration**: systemd timers

### Database
- **RDBMS**: PostgreSQL 17
- **Extensions**: 
  - pgai (AI/ML workflows)
  - pg_search (full-text search with BM25)
  - vector (embeddings, similarity search)
- **Migrations**: Alembic

### Application
- **Language**: Python 3.12
- **Package Manager**: uv
- **Framework**: FastAPI (future)
- **Database ORM**: SQLAlchemy (async)

## Deployment Model

### Co-located Indexer

**Why on the same machine?**
- Zero network latency (localhost)
- No VPN complexity for the indexer
- No egress costs
- Simpler security model
- Resource efficiency (runs only when needed)

**Trade-offs:**
- ✅ Simple, cost-effective, fast
- ✅ Easy to debug and monitor
- ❌ Single point of failure
- ❌ No auto-scaling (not needed for hourly job)

### Future: Separate API Server

When building the HTTP API, we may deploy it separately:
- Cloud Run or dedicated VPS
- Connects to DB via WireGuard VPN
- Independent scaling from indexer

## Cost Analysis

**Current Monthly Costs:**
- Hetzner VPS: €4.15
- GCP Artifact Registry: ~€1 (100 GB storage free tier)
- **Total: ~€5/month**

**Avoided Costs:**
- Cloud Run Jobs: ~€10-20/month
- VPN solutions: €5-15/month
- Cloud SQL: €50+/month

