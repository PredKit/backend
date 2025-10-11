#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "🔨 Building and deploying API..."

# GCP configuration
IMAGE_URI="europe-west3-docker.pkg.dev/predkit/main/api:latest"

# Build and push API image
echo "📦 Building Docker image..."
cd "$BACKEND_DIR"
docker build -f Dockerfile.api -t "$IMAGE_URI" .

echo "⬆️  Pushing to GCP Artifact Registry..."
docker push "$IMAGE_URI"

echo "✅ API image deployed: $IMAGE_URI"
echo ""
echo "Next steps:"
echo "  1. SSH to server and pull new image:"
echo "     ssh root@<server-ip> 'cd /opt/predkit && docker compose pull api'"
echo "  2. Or run Ansible playbook to update everything:"
echo "     cd deploy/ansible && ./run.sh"

