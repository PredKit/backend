#!/bin/bash

# GCP setup script for PredKit
set -e

PROJECT_ID="predkit"

echo "Setting up GCP for project: $PROJECT_ID"

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable artifactregistry.googleapis.com
gcloud services enable iam.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com

# Verify APIs are enabled
echo "Verifying APIs..."
gcloud services list --enabled --filter="name:(artifactregistry.googleapis.com OR iam.googleapis.com)"

echo "✅ GCP setup completed!"
