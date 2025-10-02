# GCP Artifact Registry for Docker images
resource "google_artifact_registry_repository" "main_registry" {
  location      = local.gcp_region
  repository_id = "main"
  description   = "Main Docker images repository"
  format        = "DOCKER"

  docker_config {
    immutable_tags = false  # Mutable: can overwrite tags
  }

  labels = {
    project = "predkit"
  }
}

# Service account for external services (like Hetzner VPS) to pull images
resource "google_service_account" "registry_puller" {
  account_id   = "registry-puller"
  display_name = "Registry Puller"
  description  = "Service account for pulling Docker images from Artifact Registry"
}

# Grant this service account permission to READ from our registry
resource "google_artifact_registry_repository_iam_member" "registry_reader" {
  project    = local.gcp_project_id
  location   = google_artifact_registry_repository.main_registry.location
  repository = google_artifact_registry_repository.main_registry.name
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.registry_puller.email}"
}

# Create a JSON key for this service account (so Hetzner VPS can authenticate)
resource "google_service_account_key" "registry_puller_key" {
  service_account_id = google_service_account.registry_puller.name
  key_algorithm      = "KEY_ALG_RSA_2048"  # GCP only supports RSA for service account keys
}

# Output registry info
output "registry_url" {
  value = "${local.gcp_region}-docker.pkg.dev/${local.gcp_project_id}/${google_artifact_registry_repository.main_registry.repository_id}"
}

output "registry_service_account_key" {
  value     = base64decode(google_service_account_key.registry_puller_key.private_key)
  sensitive = true
}
