#!/usr/bin/env bash
# ===========================================================================
# ZACMA PLATFORM — GOOGLE SECRET MANAGER INITIALIZATION & SECRETS SETUP
# ===========================================================================

set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:-zacma-platform}"

echo "🔐 Configuring Google Secret Manager for Project: ${PROJECT_ID}..."

# 1. Enable Secret Manager API
gcloud services enable secretmanager.googleapis.com --project="${PROJECT_ID}"

# Helper function to create or update secret
create_or_update_secret() {
    local secret_name="$1"
    local secret_value="$2"

    if [ -z "${secret_value}" ]; then
        echo "⚠️ Skipping empty secret: ${secret_name}"
        return
    fi

    if gcloud secrets describe "${secret_name}" --project="${PROJECT_ID}" >/dev/null 2>&1; then
        echo "🔄 Adding new version to secret '${secret_name}'..."
        echo -n "${secret_value}" | gcloud secrets versions add "${secret_name}" --data-file=- --project="${PROJECT_ID}"
    else
        echo "✨ Creating secret '${secret_name}'..."
        echo -n "${secret_value}" | gcloud secrets create "${secret_name}" --data-file=- --project="${PROJECT_ID}"
    fi
}

# 2. Register Platform Production Secrets
echo "🔒 Registering application production secrets..."

# Core Secrets (passed via env or prompts)
create_or_update_secret "zacma-secret-key" "${SECRET_KEY:-$(openssl rand -base64 32)}"
create_or_update_secret "zacma-jwt-secret" "${JWT_SECRET:-$(openssl rand -base64 32)}"

if [ -n "${DATABASE_URL:-}" ]; then
    create_or_update_secret "zacma-database-url" "${DATABASE_URL}"
fi

if [ -n "${GEMINI_API_KEY:-}" ]; then
    create_or_update_secret "zacma-gemini-api-key" "${GEMINI_API_KEY}"
fi

if [ -n "${CHAPA_SECRET_KEY:-}" ]; then
    create_or_update_secret "zacma-chapa-secret-key" "${CHAPA_SECRET_KEY}"
fi

if [ -n "${CHAPA_WEBHOOK_SECRET:-}" ]; then
    create_or_update_secret "zacma-chapa-webhook-secret" "${CHAPA_WEBHOOK_SECRET}"
fi

if [ -n "${TELEGRAM_BOT_TOKEN:-}" ]; then
    create_or_update_secret "zacma-telegram-bot-token" "${TELEGRAM_BOT_TOKEN}"
fi

if [ -n "${FIREBASE_PROJECT_ID:-}" ]; then
    create_or_update_secret "zacma-firebase-project-id" "${FIREBASE_PROJECT_ID}"
fi

# 3. Grant Cloud Run Default Service Account Access to Secrets
echo "🔑 Granting Cloud Run compute service account access to Secret Manager..."
PROJECT_NUMBER=$(gcloud projects describe "${PROJECT_ID}" --format='value(projectNumber)')
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor" >/dev/null 2>&1 || true

echo "✅ Secret Manager setup completed successfully!"
