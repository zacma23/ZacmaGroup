terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable Required GCP Services
resource "google_project_service" "services" {
  for_each = toset([
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "secretmanager.googleapis.com"
  ])
  service            = each.key
  disable_on_destroy = false
}

# Artifact Registry Repository for Docker images
resource "google_artifact_registry_repository" "repo" {
  depends_on    = [google_project_service.services]
  location      = var.region
  repository_id = var.artifact_repo_name
  description   = "ZACMA SaaS Platform Container Repository"
  format        = "DOCKER"
}

# Cloud Run: Backend API Service
resource "google_cloud_run_v2_service" "backend" {
  depends_on = [google_project_service.services, google_artifact_registry_repository.repo]
  name       = "zacma-backend"
  location   = var.region
  ingress    = "INGRESS_TRAFFIC_ALL"

  template {
    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_repo_name}/zacma-backend:latest"
      resources {
        limits = {
          cpu    = "1000m"
          memory = "1024Mi"
        }
      }
      ports {
        container_port = 8000
      }
      env {
        name  = "APP_ENVIRONMENT"
        value = "production"
      }
      env {
        name  = "DEMO_MODE"
        value = "false"
      }
      env {
        name  = "SUPABASE_URL"
        value = var.supabase_url
      }
      env {
        name  = "SANTIMPAY_BASE_URL"
        value = "https://services.santimpay.com/api/v1/gateway"
      }
      env {
        name  = "SANTIMPAY_TESTBED"
        value = "false"
      }
    }
  }
}

# Cloud Run: Frontend UI Service
resource "google_cloud_run_v2_service" "frontend" {
  depends_on = [google_project_service.services, google_cloud_run_v2_service.backend]
  name       = "zacma-frontend"
  location   = var.region
  ingress    = "INGRESS_TRAFFIC_ALL"

  template {
    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_repo_name}/zacma-frontend:latest"
      resources {
        limits = {
          cpu    = "1000m"
          memory = "1024Mi"
        }
      }
      ports {
        container_port = 3000
      }
      env {
        name  = "NODE_ENV"
        value = "production"
      }
      env {
        name  = "NEXT_PUBLIC_API_URL"
        value = google_cloud_run_v2_service.backend.uri
      }
      env {
        name  = "NEXT_PUBLIC_SUPABASE_URL"
        value = var.supabase_url
      }
    }
  }
}

# Allow Unauthenticated Public Ingress for Frontend and Backend
resource "google_cloud_run_v2_service_iam_member" "backend_public" {
  name     = google_cloud_run_v2_service.backend.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_v2_service_iam_member" "frontend_public" {
  name     = google_cloud_run_v2_service.frontend.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}
