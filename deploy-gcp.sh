#!/usr/bin/env bash
# ==============================================================================
# ZACMA Group - Google Cloud Run One-Click Production Deployment Script
# ==============================================================================
set -euo pipefail

# Default Configuration
PROJECT_ID="${GCP_PROJECT_ID:-$(gcloud config get-value project 2>/dev/null || echo "")}"
REGION="${GCP_REGION:-us-central1}"
ARTIFACT_REPO="${GCP_ARTIFACT_REPO:-zacma-repo}"
BACKEND_SERVICE="zacma-backend"
FRONTEND_SERVICE="zacma-frontend"

echo "======================================================================"
echo "🚀 Starting ZACMA Group Google Cloud Deployment"
echo "======================================================================"

if [[ -z "$PROJECT_ID" ]]; then
  echo "❌ Error: Google Cloud Project ID not set."
  echo "Run: gcloud config set project YOUR_PROJECT_ID or export GCP_PROJECT_ID=YOUR_PROJECT_ID"
  exit 1
fi

echo "🔹 Project: ${PROJECT_ID}"
echo "🔹 Region:  ${REGION}"
echo "🔹 Artifact Registry: ${ARTIFACT_REPO}"
echo ""

# 1. Enable Required Google Cloud APIs
echo "📦 Step 1: Enabling Required Google Cloud APIs..."
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  compute.googleapis.com \
  --project="${PROJECT_ID}"

# 2. Create Artifact Registry Repository if not exists
echo "📦 Step 2: Ensuring Artifact Registry repository exists..."
if ! gcloud artifacts repositories describe "${ARTIFACT_REPO}" --location="${REGION}" --project="${PROJECT_ID}" &>/dev/null; then
  gcloud artifacts repositories create "${ARTIFACT_REPO}" \
    --repository-format=docker \
    --location="${REGION}" \
    --description="ZACMA Platform Docker Images" \
    --project="${PROJECT_ID}"
  echo "✅ Artifact Registry repository created."
else
  echo "✅ Artifact Registry repository already exists."
fi

# 3. Submit Cloud Build
echo "📦 Step 3: Submitting Cloud Build for Backend & Frontend..."
gcloud builds submit \
  --config=cloudbuild.yaml \
  --substitutions=_REGION="${REGION}",_REPO_NAME="${ARTIFACT_REPO}",_BACKEND_SERVICE="${BACKEND_SERVICE}",_FRONTEND_SERVICE="${FRONTEND_SERVICE}" \
  --project="${PROJECT_ID}"

# 4. Retrieve Live Service URLs
echo ""
echo "======================================================================"
echo "🎉 DEPLOYMENT COMPLETE!"
echo "======================================================================"
BACKEND_URL=$(gcloud run services describe "${BACKEND_SERVICE}" --region="${REGION}" --project="${PROJECT_ID}" --format='value(status.url)')
FRONTEND_URL=$(gcloud run services describe "${FRONTEND_SERVICE}" --region="${REGION}" --project="${PROJECT_ID}" --format='value(status.url)')

echo "🌐 Frontend URL: ${FRONTEND_URL}"
echo "🔌 Backend API:  ${BACKEND_URL}"
echo "📖 API Docs:     ${BACKEND_URL}/docs"
echo "🩺 Health Check: ${BACKEND_URL}/health"
echo "======================================================================"
