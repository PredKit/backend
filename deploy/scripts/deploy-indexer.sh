#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "🔨 Building and deploying indexer..."

# GCP configuration
IMAGE_URI="europe-west3-docker.pkg.dev/predkit/main/indexer:latest"

# Build and push indexer image
echo "📦 Building Docker image..."
cd "$BACKEND_DIR"
docker build -f Dockerfile.indexer -t "$IMAGE_URI" .

echo "⬆️  Pushing to GCP Artifact Registry..."
docker push "$IMAGE_URI"

echo "✅ Indexer image deployed: $IMAGE_URI"
echo ""
echo "Next steps:"
echo "  1. SSH to server and pull new image:"
echo "     ssh root@<server-ip> 'cd /opt/predkit && docker compose pull indexer'"
echo "  2. Or run Ansible playbook to update everything:"
echo "     cd deploy/ansible && ./run.sh"

