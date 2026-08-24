#!/usr/bin/env bash
# ===========================================================================
# ZACMA PLATFORM — GOOGLE CLOUD RUN STAGING DEPLOYMENT SCRIPT
# ===========================================================================

set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:-zacma-platform}"
REGION="${GCP_REGION:-us-central1}"
BACKEND_SERVICE="zacma-backend"
FRONTEND_SERVICE="zacma-frontend"
ARTIFACT_REPO="zacma-containers"

echo "🚀 Starting Google Cloud Run Staging Deployment for Project: ${PROJECT_ID} (Region: ${REGION})"

# 1. Ensure Artifact Registry repository exists
gcloud artifacts repositories describe "${ARTIFACT_REPO}" \
    --project="${PROJECT_ID}" \
    --location="${REGION}" >/dev/null 2>&1 || \
gcloud artifacts repositories create "${ARTIFACT_REPO}" \
    --repository-format=docker \
    --location="${REGION}" \
    --project="${PROJECT_ID}" \
    --description="ZACMA Docker images"

# 2. Build & Deploy Backend API
echo "📦 Building and deploying Backend API to Cloud Run..."
BACKEND_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REPO}/backend:staging"

gcloud builds submit ../../backend \
    --tag="${BACKEND_IMAGE}" \
    --project="${PROJECT_ID}"

gcloud run deploy "${BACKEND_SERVICE}" \
    --image="${BACKEND_IMAGE}" \
    --platform=managed \
    --region="${REGION}" \
    --project="${PROJECT_ID}" \
    --allow-unauthenticated \
    --min-instances=0 \
    --max-instances=5 \
    --memory=512Mi \
    --cpu=1 \
    --set-env-vars="APP_ENV=staging,DEMO_MODE=true,AI_PROVIDER=gemini,STORAGE_PROVIDER=local,GCP_PROJECT_ID=${PROJECT_ID}"

BACKEND_URL=$(gcloud run services describe "${BACKEND_SERVICE}" --platform=managed --region="${REGION}" --project="${PROJECT_ID}" --format='value(status.url)')
echo "✅ Backend API running at: ${BACKEND_URL}"

# 3. Build & Deploy Next.js Frontend
echo "📦 Building and deploying Frontend Dashboard to Cloud Run..."
FRONTEND_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REPO}/frontend:staging"

gcloud builds submit ../../dashboard \
    --tag="${FRONTEND_IMAGE}" \
    --project="${PROJECT_ID}"

gcloud run deploy "${FRONTEND_SERVICE}" \
    --image="${FRONTEND_IMAGE}" \
    --platform=managed \
    --region="${REGION}" \
    --project="${PROJECT_ID}" \
    --allow-unauthenticated \
    --min-instances=0 \
    --max-instances=5 \
    --memory=512Mi \
    --cpu=1 \
    --set-env-vars="NEXT_PUBLIC_API_URL=${BACKEND_URL}"

FRONTEND_URL=$(gcloud run services describe "${FRONTEND_SERVICE}" --platform=managed --region="${REGION}" --project="${PROJECT_ID}" --format='value(status.url)')
echo "✅ Frontend running at: ${FRONTEND_URL}"

echo "🎉 Deployment to Google Cloud Staging complete!"
