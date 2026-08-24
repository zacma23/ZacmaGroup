#!/usr/bin/env bash
# ===========================================================================
# ZACMA PLATFORM — CLOUD RUN CUSTOM DOMAINS MAPPING & DNS CONFIGURATION
# ===========================================================================

set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:-zacma-platform}"
REGION="${GCP_REGION:-us-central1}"
FRONTEND_SERVICE="zacma-frontend"
BACKEND_SERVICE="zacma-backend"

MAIN_DOMAIN="zacmagroup.com"
WWW_DOMAIN="www.zacmagroup.com"
API_DOMAIN="api.zacmagroup.com"

echo "🌐 Setting up Custom Domain Mappings on Cloud Run (Project: ${PROJECT_ID}, Region: ${REGION})..."

# Helper to create domain mapping
map_domain() {
    local service_name="$1"
    local domain_name="$2"

    echo "🔗 Mapping domain '${domain_name}' to Cloud Run service '${service_name}'..."
    gcloud beta run domain-mappings describe --domain="${domain_name}" --region="${REGION}" --project="${PROJECT_ID}" >/dev/null 2>&1 || \
    gcloud beta run domain-mappings create \
        --service="${service_name}" \
        --domain="${domain_name}" \
        --region="${REGION}" \
        --project="${PROJECT_ID}"
}

# 1. Map Frontend Domains
map_domain "${FRONTEND_SERVICE}" "${MAIN_DOMAIN}"
map_domain "${FRONTEND_SERVICE}" "${WWW_DOMAIN}"

# 2. Map Backend API Domain
map_domain "${BACKEND_SERVICE}" "${API_DOMAIN}"

echo ""
echo "======================================================================"
echo "📋 REQUIRED DNS RECORDS TO ADD TO YOUR DNS PROVIDER (Cloudflare/Namecheap/DNS)"
echo "======================================================================"
echo ""
echo "Domain: ${MAIN_DOMAIN} (Main Frontend)"
echo "----------------------------------------------------------------------"
gcloud beta run domain-mappings describe --domain="${MAIN_DOMAIN}" --region="${REGION}" --project="${PROJECT_ID}" --format='table(resourceRecords[].type,resourceRecords[].name,resourceRecords[].rrdata)' || true

echo ""
echo "Domain: ${WWW_DOMAIN} (WWW Frontend)"
echo "----------------------------------------------------------------------"
gcloud beta run domain-mappings describe --domain="${WWW_DOMAIN}" --region="${REGION}" --project="${PROJECT_ID}" --format='table(resourceRecords[].type,resourceRecords[].name,resourceRecords[].rrdata)' || true

echo ""
echo "Domain: ${API_DOMAIN} (Backend API)"
echo "----------------------------------------------------------------------"
gcloud beta run domain-mappings describe --domain="${API_DOMAIN}" --region="${REGION}" --project="${PROJECT_ID}" --format='table(resourceRecords[].type,resourceRecords[].name,resourceRecords[].rrdata)' || true

echo ""
echo "✅ Custom domain mapping setup complete! Google Cloud will automatically provision free SSL certificates."
