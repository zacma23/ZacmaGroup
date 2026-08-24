#!/usr/bin/env bash
# ===========================================================================
# ZACMA PLATFORM — GOOGLE CLOUD SQL POSTGRESQL PROVISIONING & SECURITY SETUP
# ===========================================================================

set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:-zacma-platform}"
REGION="${GCP_REGION:-us-central1}"
INSTANCE_NAME="${GCP_SQL_INSTANCE:-zacma-postgres-staging}"
DB_NAME="${GCP_DB_NAME:-zacma}"
DB_USER="${GCP_DB_USER:-zacma_app}"
DB_TIER="${GCP_SQL_TIER:-db-f1-micro}" # Cost-effective tier for staging/test

echo "🗄️ Initializing Google Cloud SQL for PostgreSQL (Project: ${PROJECT_ID}, Region: ${REGION})..."

# 1. Enable Cloud SQL Admin API
gcloud services enable sqladmin.googleapis.com --project="${PROJECT_ID}"

# 2. Create PostgreSQL Instance if it does not already exist
if gcloud sql instances describe "${INSTANCE_NAME}" --project="${PROJECT_ID}" >/dev/null 2>&1; then
    echo "ℹ️ Cloud SQL instance '${INSTANCE_NAME}' already exists."
else
    echo "🚀 Creating Cloud SQL PostgreSQL 15 instance: ${INSTANCE_NAME}..."
    gcloud sql instances create "${INSTANCE_NAME}" \
        --project="${PROJECT_ID}" \
        --database-version=POSTGRES_15 \
        --tier="${DB_TIER}" \
        --region="${REGION}" \
        --storage-type=SSD \
        --storage-size=10GB \
        --storage-auto-increase \
        --backup-start-time=02:00 \
        --enable-point-in-time-recovery \
        --maintenance-window-day=SUN \
        --maintenance-window-hour=04 \
        --database-flags=max_connections=100
fi

# 3. Create Application Database
echo "📦 Ensuring database '${DB_NAME}' exists..."
gcloud sql databases describe "${DB_NAME}" --instance="${INSTANCE_NAME}" --project="${PROJECT_ID}" >/dev/null 2>&1 || \
gcloud sql databases create "${DB_NAME}" --instance="${INSTANCE_NAME}" --project="${PROJECT_ID}"

# 4. Generate/Configure Secure Application Database User
echo "🔐 Configuring application database user '${DB_USER}'..."
DB_PASS=$(openssl rand -base64 24 | tr -d '/+=')

gcloud sql users describe "${DB_USER}" "%" --instance="${INSTANCE_NAME}" --project="${PROJECT_ID}" >/dev/null 2>&1 || \
gcloud sql users create "${DB_USER}" \
    --instance="${INSTANCE_NAME}" \
    --project="${PROJECT_ID}" \
    --password="${DB_PASS}"

# 5. Store DB Connection String in Google Secret Manager
echo "🔒 Registering DATABASE_URL in Secret Manager..."
CONNECTION_NAME=$(gcloud sql instances describe "${INSTANCE_NAME}" --project="${PROJECT_ID}" --format='value(connectionName)')
SECRET_NAME="zacma-database-url"
SECRET_VAL="postgresql://${DB_USER}:${DB_PASS}@/${DB_NAME}?host=/cloudsql/${CONNECTION_NAME}"

echo -n "${SECRET_VAL}" | gcloud secrets create "${SECRET_NAME}" --data-file=- --project="${PROJECT_ID}" 2>/dev/null || \
echo -n "${SECRET_VAL}" | gcloud secrets versions add "${SECRET_NAME}" --data-file=- --project="${PROJECT_ID}"

echo "✅ Google Cloud SQL setup complete! Connection Name: ${CONNECTION_NAME}"
