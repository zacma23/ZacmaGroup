#!/usr/bin/env bash
# ==============================================================================
# ZACMA Group - Google Cloud Run One-Click Production Deployment Script
# ==============================================================================
set -euo pipefail

# Default Configuration
PROJECT_ID="${GCP_PROJECT_ID:-zacmagroupaiautomation}"
PROJECT_NUMBER="${GCP_PROJECT_NUMBER:-659536564001}"
REGION="${GCP_REGION:-us-central1}"
ARTIFACT_REPO="${GCP_ARTIFACT_REPO:-zacma-repo}"
BACKEND_SERVICE="zacma-backend"
FRONTEND_SERVICE="zacma-frontend"

echo "======================================================================"
echo "🚀 Starting ZACMA Group Google Cloud Deployment"
echo "======================================================================"

echo "🔹 Project: ${PROJECT_ID}"
echo "🔹 Project Number: ${PROJECT_NUMBER}"
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

# 4. Ensure Public Invocation Permissions
echo "📦 Step 4: Configuring Public IAM Access for Cloud Run Services..."
gcloud run services add-iam-policy-binding "${BACKEND_SERVICE}" \
  --region="${REGION}" \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --project="${PROJECT_ID}" --quiet || true

gcloud run services add-iam-policy-binding "${FRONTEND_SERVICE}" \
  --region="${REGION}" \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --project="${PROJECT_ID}" --quiet || true

# 5. Retrieve and Display Live Service URLs
echo ""
echo "======================================================================"
echo "🎉 DEPLOYMENT COMPLETE!"
echo "======================================================================"
BACKEND_URL=$(gcloud run services describe "${BACKEND_SERVICE}" --region="${REGION}" --project="${PROJECT_ID}" --format='value(status.url)')
FRONTEND_URL=$(gcloud run services describe "${FRONTEND_SERVICE}" --region="${REGION}" --project="${PROJECT_ID}" --format='value(status.url)')

echo "🌐 Live Frontend URL: ${FRONTEND_URL}"
echo "🔌 Live Backend API:  ${BACKEND_URL}"
echo "📖 Live API Docs:     ${BACKEND_URL}/docs"
echo "🩺 Live Health Check: ${BACKEND_URL}/health"
echo "======================================================================"
