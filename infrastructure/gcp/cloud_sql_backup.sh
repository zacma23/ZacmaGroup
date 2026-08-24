#!/usr/bin/env bash
# ===========================================================================
# ZACMA PLATFORM — GOOGLE CLOUD SQL BACKUP & RESTORE UTILITY
# ===========================================================================

set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:-zacma-platform}"
INSTANCE_NAME="${GCP_SQL_INSTANCE:-zacma-postgres-staging}"
STORAGE_BUCKET="${GCP_BACKUP_BUCKET:-zacma-db-backups-${PROJECT_ID}}"

ACTION="${1:-backup}" # 'backup', 'list', 'export'

case "${ACTION}" in
    backup)
        echo "💾 Triggering on-demand automated backup for instance: ${INSTANCE_NAME}..."
        DESCRIPTION="manual-backup-$(date +%Y%m%d-%H%M%S)"
        gcloud sql backups create \
            --instance="${INSTANCE_NAME}" \
            --project="${PROJECT_ID}" \
            --description="${DESCRIPTION}"
        echo "✅ Backup created successfully: ${DESCRIPTION}"
        ;;
    list)
        echo "📋 Listing available backups for instance: ${INSTANCE_NAME}..."
        gcloud sql backups list \
            --instance="${INSTANCE_NAME}" \
            --project="${PROJECT_ID}"
        ;;
    export)
        EXPORT_FILE="gs://${STORAGE_BUCKET}/zacma-db-dump-$(date +%Y%m%d-%H%M%S).sql.gz"
        echo "📦 Exporting full database to ${EXPORT_FILE}..."
        gcloud sql export sql "${INSTANCE_NAME}" "${EXPORT_FILE}" \
            --database=zacma \
            --project="${PROJECT_ID}"
        echo "✅ Export complete!"
        ;;
    *)
        echo "Usage: $0 [backup|list|export]"
        exit 1
        ;;
esac
