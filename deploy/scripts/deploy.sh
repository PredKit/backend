#!/bin/bash
# Complete deployment script for PredKit
# Builds all images, pushes to registry, and deploys to production

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "🚀 PredKit Full Deployment"
echo "=========================="
echo ""

# GCP configuration
REGISTRY_HOST="europe-west3-docker.pkg.dev"
PROJECT="predkit"
REPO="main"

# Check if we're in the right directory
if [ ! -f "$BACKEND_DIR/pyproject.toml" ]; then
    echo "❌ Error: Must run from backend directory structure"
    exit 1
fi

# Build and push all images
echo "📦 Building and pushing Docker images..."
echo ""

# 1. Build and push API
echo "🔨 Building API image..."
cd "$BACKEND_DIR"
API_IMAGE="$REGISTRY_HOST/$PROJECT/$REPO/api:latest"
docker build -f Dockerfile.api -t "$API_IMAGE" .
echo "⬆️  Pushing API image..."
docker push "$API_IMAGE"
echo "✅ API deployed: $API_IMAGE"
echo ""

# 2. Build and push Indexer
echo "🔨 Building Indexer image..."
INDEXER_IMAGE="$REGISTRY_HOST/$PROJECT/$REPO/indexer:latest"
docker build -f Dockerfile.indexer -t "$INDEXER_IMAGE" .
echo "⬆️  Pushing Indexer image..."
docker push "$INDEXER_IMAGE"
echo "✅ Indexer deployed: $INDEXER_IMAGE"
echo ""

# 3. Run Ansible to update production server
echo "🔧 Deploying to production server..."
echo ""

cd "$BACKEND_DIR/deploy/ansible"

# Get server IP from Terraform
cd ../terraform
SERVER_IP=$(terraform output -raw database_ip 2>/dev/null || echo "")

if [ -z "$SERVER_IP" ]; then
    echo "⚠️  Warning: Could not get server IP from Terraform"
    echo "Please enter server IP manually:"
    read -p "Server IP: " SERVER_IP
fi

echo "Target server: $SERVER_IP"

# Generate service account key for Ansible
terraform output -raw registry_service_account_key > service-key.json 2>/dev/null || true

# Go back to Ansible directory
cd ../ansible

# Run the Ansible playbook
echo ""
echo "Running Ansible playbook to update server..."
ansible-playbook -i inventory.yml setup-database.yml \
  --extra-vars "server_ip=$SERVER_IP" \
  --ask-vault-pass

echo ""
echo "🎉 Deployment Complete!"
echo "======================"
echo ""
echo "Deployed components:"
echo "  ✅ API image: $API_IMAGE"
echo "  ✅ Indexer image: $INDEXER_IMAGE"
echo "  ✅ Production server: $SERVER_IP"
echo ""
echo "Check deployment status:"
echo "  ssh root@$SERVER_IP 'cd /opt/predkit && docker compose ps'"
echo "  ssh root@$SERVER_IP 'cd /opt/predkit && docker compose logs -f api'"
echo "  ssh root@$SERVER_IP 'cd /opt/predkit && docker compose logs -f vectorizer'"
echo ""
echo "API endpoint: https://api.predkit.com"

