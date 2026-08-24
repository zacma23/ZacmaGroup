#!/usr/bin/env bash
# ===========================================================================
# ZACMA PLATFORM — UNIFIED GOOGLE CLOUD STAGING DEPLOYMENT ORCHESTRATOR
# ===========================================================================
# Runs preflight automated tests, ensures all GCP services are provisioned,
# builds container images, and deploys Backend API & Next.js Frontend to Cloud Run.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

PROJECT_ID="${GCP_PROJECT_ID:-zacma-platform}"
REGION="${GCP_REGION:-us-central1}"

echo "======================================================================"
echo "🚀 ZACMA PLATFORM — GOOGLE CLOUD STAGING DEPLOYMENT"
echo "Project ID: ${PROJECT_ID} | Region: ${REGION}"
echo "======================================================================"

# Step 1: Pre-Flight Automated Verification
echo "🧪 Running pre-flight automated pytest suite..."
cd "${ROOT_DIR}/backend"
if [ -d ".venv" ]; then
    source .venv/bin/activate || source .venv/Scripts/activate || true
fi
python3 -m pytest tests/ -v || python -m pytest tests/ -v
echo "✅ All backend tests passed!"

# Step 2: Provision Core Google Cloud Resources (Storage, Pub/Sub, Workflows)
echo "☁️ Provisioning GCP infrastructure (Storage, Pub/Sub, Workflows)..."
cd "${SCRIPT_DIR}"
./gcp_setup.sh

# Step 3: Deploy Cloud Run Services
echo "🚀 Deploying Cloud Run Services..."
./deploy_cloud_run.sh

echo "======================================================================"
echo "🎉 ZACMA PLATFORM STAGING DEPLOYMENT SUCCEEDED!"
echo "======================================================================"
