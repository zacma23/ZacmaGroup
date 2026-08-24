#!/usr/bin/env bash
# ===========================================================================
# ZACMA PLATFORM — GOOGLE CLOUD INITIAL SETUP & RESOURCE PROVISIONING
# ===========================================================================

set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:-zacma-platform}"
REGION="${GCP_REGION:-us-central1}"
STORAGE_BUCKET="${GCP_STORAGE_BUCKET:-zacma-private-documents-${PROJECT_ID}}"
PUBSUB_TOPIC="${GCP_PUBSUB_TOPIC:-zacma-platform-events}"

echo "🔧 Initializing Google Cloud Platform for Project: ${PROJECT_ID}..."

# 1. Enable Required Cloud APIs
echo "📡 Enabling Google Cloud APIs..."
gcloud services enable \
    run.googleapis.com \
    sqladmin.googleapis.com \
    storage.googleapis.com \
    pubsub.googleapis.com \
    workflows.googleapis.com \
    secretmanager.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    --project="${PROJECT_ID}"

# 2. Create Private Google Cloud Storage Bucket
echo "🪣 Creating Private Cloud Storage bucket: ${STORAGE_BUCKET}..."
gcloud storage buckets describe "gs://${STORAGE_BUCKET}" --project="${PROJECT_ID}" >/dev/null 2>&1 || \
gcloud storage buckets create "gs://${STORAGE_BUCKET}" \
    --project="${PROJECT_ID}" \
    --location="${REGION}" \
    --uniform-bucket-level-access

# 3. Create Pub/Sub Topic & Subscription
echo "📨 Creating Pub/Sub topic: ${PUBSUB_TOPIC}..."
gcloud pubsub topics describe "${PUBSUB_TOPIC}" --project="${PROJECT_ID}" >/dev/null 2>&1 || \
gcloud pubsub topics create "${PUBSUB_TOPIC}" --project="${PROJECT_ID}"

gcloud pubsub subscriptions describe "${PUBSUB_TOPIC}-sub" --project="${PROJECT_ID}" >/dev/null 2>&1 || \
gcloud pubsub subscriptions create "${PUBSUB_TOPIC}-sub" \
    --topic="${PUBSUB_TOPIC}" \
    --project="${PROJECT_ID}"

# 4. Deploy Google Cloud Workflows
echo "⚡ Deploying Service Fulfillment Workflow..."
gcloud workflows deploy service_fulfillment \
    --source=workflows/service_fulfillment.yaml \
    --location="${REGION}" \
    --project="${PROJECT_ID}"

echo "✅ Google Cloud Platform setup completed successfully!"
