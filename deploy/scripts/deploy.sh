#!/bin/bash

# Deployment script for PredKit backend
set -e

ENVIRONMENT=${1:-dev}

echo "Deploying PredKit backend to $ENVIRONMENT environment..."

# Deploy database infrastructure only
echo "Deploying database infrastructure..."
cd ../terraform
terraform init
terraform plan -var="environment=$ENVIRONMENT"
terraform apply -var="environment=$ENVIRONMENT" -auto-approve

echo "Database deployment completed!"
echo "Database connection details:"
terraform output database_connection_string
echo ""
echo "Next steps:"
echo "1. Test database connection"
echo "2. Run database migrations if needed"
echo "3. Deploy functions later when ready"
