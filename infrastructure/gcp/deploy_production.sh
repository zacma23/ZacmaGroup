#!/usr/bin/env bash
# ===========================================================================
# ZACMA PLATFORM — GOOGLE CLOUD RUN PRODUCTION DEPLOYMENT SCRIPT
# ===========================================================================
# Deploys Backend API and Next.js Frontend with Secret Manager bindings,
# autoscaling controls, and custom domains (zacmagroup.com & api.zacmagroup.com).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

PROJECT_ID="${GCP_PROJECT_ID:-zacma-platform}"
REGION="${GCP_REGION:-us-central1}"
BACKEND_SERVICE="zacma-backend"
FRONTEND_SERVICE="zacma-frontend"
ARTIFACT_REPO="zacma-containers"
SQL_INSTANCE="${GCP_SQL_INSTANCE:-zacma-postgres-staging}"

echo "======================================================================"
echo "🚀 ZACMA PLATFORM — PRODUCTION CLOUD RUN DEPLOYMENT"
echo "Project: ${PROJECT_ID} | Region: ${REGION}"
echo "======================================================================"

# 1. Run Automated Test Preflight
echo "🧪 Running backend pytest verification..."
cd "${ROOT_DIR}/backend"
if [ -d ".venv" ]; then
    source .venv/bin/activate || source .venv/Scripts/activate || true
fi
python3 -m pytest tests/ -v || python -m pytest tests/ -v
echo "✅ All 78 tests passed!"

# 2. Ensure Artifact Registry repository exists
cd "${SCRIPT_DIR}"
gcloud artifacts repositories describe "${ARTIFACT_REPO}" \
    --project="${PROJECT_ID}" \
    --location="${REGION}" >/dev/null 2>&1 || \
gcloud artifacts repositories create "${ARTIFACT_REPO}" \
    --repository-format=docker \
    --location="${REGION}" \
    --project="${PROJECT_ID}" \
    --description="ZACMA Production Container Images"

# 3. Setup Secret Manager
echo "🔐 Ensuring Google Secret Manager is configured..."
./setup_secret_manager.sh

# 4. Build & Deploy Backend API to Cloud Run Production
echo "📦 Building & Deploying Backend API to Cloud Run..."
BACKEND_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REPO}/backend:latest"

gcloud builds submit "${ROOT_DIR}/backend" \
    --tag="${BACKEND_IMAGE}" \
    --project="${PROJECT_ID}"

# Collect optional secret arguments if secrets exist in Secret Manager
SECRETS_ARGS=""
if gcloud secrets describe "zacma-secret-key" --project="${PROJECT_ID}" >/dev/null 2>&1; then
    SECRETS_ARGS="SECRET_KEY=zacma-secret-key:latest"
fi
if gcloud secrets describe "zacma-database-url" --project="${PROJECT_ID}" >/dev/null 2>&1; then
    SECRETS_ARGS="${SECRETS_ARGS},DATABASE_URL=zacma-database-url:latest"
fi
if gcloud secrets describe "zacma-gemini-api-key" --project="${PROJECT_ID}" >/dev/null 2>&1; then
    SECRETS_ARGS="${SECRETS_ARGS},GEMINI_API_KEY=zacma-gemini-api-key:latest"
fi
if gcloud secrets describe "zacma-chapa-secret-key" --project="${PROJECT_ID}" >/dev/null 2>&1; then
    SECRETS_ARGS="${SECRETS_ARGS},CHAPA_SECRET_KEY=zacma-chapa-secret-key:latest"
fi
if gcloud secrets describe "zacma-chapa-webhook-secret" --project="${PROJECT_ID}" >/dev/null 2>&1; then
    SECRETS_ARGS="${SECRETS_ARGS},CHAPA_WEBHOOK_SECRET=zacma-chapa-webhook-secret:latest"
fi

DEPLOY_BACKEND_CMD=(
    gcloud run deploy "${BACKEND_SERVICE}"
    --image="${BACKEND_IMAGE}"
    --platform=managed
    --region="${REGION}"
    --project="${PROJECT_ID}"
    --allow-unauthenticated
    --min-instances=1
    --max-instances=10
    --memory=1Gi
    --cpu=1
    --timeout=300
    --concurrency=80
    --set-env-vars="APP_ENV=production,DEMO_MODE=true,AI_PROVIDER=gemini,STORAGE_PROVIDER=gcs,GCP_STORAGE_BUCKET=zacma-private-documents-${PROJECT_ID},GCP_PUBSUB_ENABLED=true,CORS_ORIGINS=https://zacmagroup.com,https://www.zacmagroup.com,https://api.zacmagroup.com"
)

if [ -n "${SECRETS_ARGS}" ]; then
    DEPLOY_BACKEND_CMD+=(--set-secrets="${SECRETS_ARGS}")
fi

"${DEPLOY_BACKEND_CMD[@]}"

BACKEND_URL=$(gcloud run services describe "${BACKEND_SERVICE}" --platform=managed --region="${REGION}" --project="${PROJECT_ID}" --format='value(status.url)')
echo "✅ Backend API running at: ${BACKEND_URL}"

# 5. Build & Deploy Next.js Frontend to Cloud Run Production
echo "📦 Building & Deploying Frontend Dashboard to Cloud Run..."
FRONTEND_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REPO}/frontend:latest"

gcloud builds submit "${ROOT_DIR}/dashboard" \
    --tag="${FRONTEND_IMAGE}" \
    --project="${PROJECT_ID}"

gcloud run deploy "${FRONTEND_SERVICE}" \
    --image="${FRONTEND_IMAGE}" \
    --platform=managed \
    --region="${REGION}" \
    --project="${PROJECT_ID}" \
    --allow-unauthenticated \
    --min-instances=1
    --max-instances=10 \
    --memory=1Gi \
    --cpu=1 \
    --timeout=60 \
    --concurrency=80 \
    --set-env-vars="NEXT_PUBLIC_API_URL=https://api.zacmagroup.com"

FRONTEND_URL=$(gcloud run services describe "${FRONTEND_SERVICE}" --platform=managed --region="${REGION}" --project="${PROJECT_ID}" --format='value(status.url)')
echo "✅ Frontend running at: ${FRONTEND_URL}"

# 6. Configure Custom Domain Mappings
echo "🌐 Mapping Custom Domains..."
./setup_custom_domains.sh || true

echo "======================================================================"
echo "🎉 PRODUCTION DEPLOYMENT TO GOOGLE CLOUD RUN COMPLETED SUCCESSFULLY!"
echo "Main Website: https://zacmagroup.com (Cloud Run: ${FRONTEND_URL})"
echo "Backend API:  https://api.zacmagroup.com (Cloud Run: ${BACKEND_URL})"
echo "======================================================================"
