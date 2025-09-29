#!/bin/bash

# Script to run Ansible playbook with server IP from Terraform

set -e

# Get server IP from Terraform
cd ../terraform
SERVER_IP=$(terraform output -raw database_ip)
echo "Database server IP: $SERVER_IP"

# Generate service account key for Ansible to copy
terraform output -raw registry_service_account_key > service-key.json

# Go back to Ansible directory
cd ../ansible

# Run the playbook
echo "Running Ansible playbook..."
ansible-playbook -i inventory.yml setup-database.yml \
  --extra-vars "server_ip=$SERVER_IP" \
  --ask-vault-pass

echo "✅ Database server configuration completed!"
echo "You can check the service with:"
echo "  ssh root@$SERVER_IP 'systemctl status predkit-stack'"
echo "  ssh root@$SERVER_IP 'journalctl -u predkit-stack -f'"
