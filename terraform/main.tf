terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.4.0"
    }
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "~> 1.53.1"
    }
  }
}

# Configuration
locals {
  gcp_project_id = "predkit"
  gcp_region     = "europe-west3" # Frankfurt
  hetzner_location = "fsn1"  # Falkenstein
}

# GCP Provider (for Artifact Registry)
provider "google" {
  project = local.gcp_project_id
  region  = local.gcp_region
}

# Hetzner Cloud Provider
provider "hcloud" {
  token = var.hetzner_token
}

# Variables (only for sensitive/changeable stuff)
variable "hetzner_token" {
  description = "Hetzner Cloud API Token"
  type        = string
  sensitive   = true
}
