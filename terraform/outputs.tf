output "backend_url" {
  value       = google_cloud_run_v2_service.backend.uri
  description = "Google Cloud Run Backend API URL"
}

output "frontend_url" {
  value       = google_cloud_run_v2_service.frontend.uri
  description = "Google Cloud Run Frontend Dashboard URL"
}

output "artifact_registry_repo" {
  value       = google_artifact_registry_repository.repo.id
  description = "Artifact Registry Repository ID"
}
