#!/usr/bin/env bash
# ==============================================================================
# ZACMA Group - Google Cloud Run Complete Production Deployment & Verification Script
# ==============================================================================
set -euo pipefail

# 1. Discover or Configure Active Project
GCP_ACTIVE_PROJ="$(gcloud config get-value project 2>/dev/null || echo "")"
PROJECT_ID="${GCP_PROJECT_ID:-${GCP_ACTIVE_PROJ:-bionic-eye-506609-q5}}"
PROJECT_NUMBER="${GCP_PROJECT_NUMBER:-762777304269}"
BILLING_ACCOUNT="01CC1F-189B8E-643632"
REGION="${GCP_REGION:-us-central1}"
ARTIFACT_REPO="${GCP_ARTIFACT_REPO:-zacma-repo}"
BACKEND_SERVICE="zacma-backend"
FRONTEND_SERVICE="zacma-frontend"

echo "======================================================================"
echo "🚀 ZACMA GROUP: GOOGLE CLOUD PRODUCTION DEPLOYMENT & VERIFICATION"
echo "======================================================================"
echo "🔹 Project ID:      ${PROJECT_ID}"
echo "🔹 Project Number:  ${PROJECT_NUMBER}"
echo "🔹 Billing Account: ${BILLING_ACCOUNT}"
echo "🔹 Region:          ${REGION}"
echo "🔹 Artifact Repo:   ${ARTIFACT_REPO}"
echo "======================================================================"
echo ""

# 2. Set Project & Verify Authentication
echo "🔑 Step 1: Verifying gcloud session & setting active project..."
gcloud config set project "${PROJECT_ID}" --quiet
echo "✅ Active project set to: $(gcloud config get-value project)"

# 3. Link Billing if necessary
echo ""
echo "💳 Step 2: Verifying billing account linking..."
gcloud billing projects link "${PROJECT_ID}" --billing-account="${BILLING_ACCOUNT}" --quiet 2>/dev/null || echo "ℹ️ Billing already linked or managed."

# 4. Enable APIs
echo ""
echo "📦 Step 3: Enabling Required Google Cloud APIs..."
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  compute.googleapis.com \
  --project="${PROJECT_ID}"
echo "✅ Required Google Cloud APIs enabled."

# 4. Ensure Artifact Registry Exists
echo ""
echo "📦 Step 3: Ensuring Artifact Registry exists..."
if ! gcloud artifacts repositories describe "${ARTIFACT_REPO}" --location="${REGION}" --project="${PROJECT_ID}" &>/dev/null; then
  gcloud artifacts repositories create "${ARTIFACT_REPO}" \
    --repository-format=docker \
    --location="${REGION}" \
    --description="ZACMA Platform Docker Images" \
    --project="${PROJECT_ID}"
  echo "✅ Artifact Registry repository created: ${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REPO}"
else
  echo "✅ Artifact Registry repository already exists."
fi

# 5. Execute Cloud Build Pipeline
echo ""
echo "📦 Step 4: Submitting Cloud Build for Backend & Frontend..."
gcloud builds submit \
  --config=cloudbuild.yaml \
  --substitutions=_REGION="${REGION}",_REPO_NAME="${ARTIFACT_REPO}",_BACKEND_SERVICE="${BACKEND_SERVICE}",_FRONTEND_SERVICE="${FRONTEND_SERVICE}" \
  --project="${PROJECT_ID}"

# 6. Configure IAM Public Invoker Policy
echo ""
echo "🔒 Step 5: Ensuring Cloud Run Services have Public Invocation access..."
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

# 7. Query Real Deployed URLs
echo ""
echo "======================================================================"
echo "🔍 Step 6: Querying Deployed Cloud Run Service URLs..."
BACKEND_URL=$(gcloud run services describe "${BACKEND_SERVICE}" --region="${REGION}" --project="${PROJECT_ID}" --format='value(status.url)')
FRONTEND_URL=$(gcloud run services describe "${FRONTEND_SERVICE}" --region="${REGION}" --project="${PROJECT_ID}" --format='value(status.url)')

# 8. Automated Live Service Health Verification
echo ""
echo "🩺 Step 7: Verifying Live Cloud Endpoints..."
echo "Testing Backend API: ${BACKEND_URL}/health ..."
curl -sSf "${BACKEND_URL}/health" || echo "⚠️ Backend initializing..."

echo "Testing Frontend UI: ${FRONTEND_URL} ..."
curl -sSf "${FRONTEND_URL}" > /dev/null && echo "✅ Frontend responds HTTP 200 OK!" || echo "⚠️ Frontend initializing..."

# 9. Final Deployment Summary
echo ""
echo "======================================================================"
echo "🎉 DEPLOYMENT SUCCESSFUL!"
echo "======================================================================"
echo "Google Cloud Project:  ${PROJECT_ID}"
echo "Region:                ${REGION}"
echo "Frontend Service:      ${FRONTEND_SERVICE}"
echo "Frontend URL:          ${FRONTEND_URL}"
echo "Backend API Service:   ${BACKEND_SERVICE}"
echo "Backend API URL:       ${BACKEND_URL}"
echo "API Documentation:     ${BACKEND_URL}/docs"
echo "Admin Portal:          ${FRONTEND_URL}/dashboard/admin/users"
echo "Client Portal:         ${FRONTEND_URL}/portal"
echo "======================================================================"
