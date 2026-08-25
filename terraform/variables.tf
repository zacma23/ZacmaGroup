variable "project_id" {
  type        = string
  default     = "bionic-eye-506609-q5"
  description = "Google Cloud Project ID"
}

variable "region" {
  type        = string
  default     = "us-central1"
  description = "Google Cloud Region"
}

variable "artifact_repo_name" {
  type        = string
  default     = "zacma-repo"
  description = "Artifact Registry Docker repository name"
}

variable "supabase_url" {
  type        = string
  default     = "https://ihuxlbfqevubzsqebszp.supabase.co"
  description = "Production Supabase Database URL"
}
