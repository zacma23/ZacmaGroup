# ==============================================================================
# ZACMA Group - Google Cloud Run One-Click Production Deployment Script (PowerShell)
# ==============================================================================
param (
    [string]$ProjectId = $(if ($env:GCP_PROJECT_ID) { $env:GCP_PROJECT_ID } else { "bionic-eye-506609-q5" }),
    [string]$Region = "us-central1",
    [string]$ArtifactRepo = "zacma-repo"
)

$ErrorActionPreference = "Stop"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "🚀 Starting ZACMA Group Google Cloud Deployment (PowerShell)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

if (-not $ProjectId) {
    try {
        $ProjectId = (gcloud config get-value project 2>$null)
    } catch {}
}

if (-not $ProjectId) {
    Write-Host "❌ Error: Google Cloud Project ID not set." -ForegroundColor Red
    Write-Host "Run: gcloud config set project YOUR_PROJECT_ID or pass -ProjectId YOUR_PROJECT_ID" -ForegroundColor Yellow
    exit 1
}

Write-Host "🔹 Project: $ProjectId" -ForegroundColor Green
Write-Host "🔹 Region:  $Region" -ForegroundColor Green
Write-Host "🔹 Artifact Registry: $ArtifactRepo" -ForegroundColor Green
Write-Host ""

# 1. Enable APIs
Write-Host "📦 Step 1: Enabling Required Google Cloud APIs..." -ForegroundColor Yellow
gcloud services enable `
    run.googleapis.com `
    artifactregistry.googleapis.com `
    cloudbuild.googleapis.com `
    secretmanager.googleapis.com `
    compute.googleapis.com `
    --project=$ProjectId

# 2. Artifact Registry
Write-Host "📦 Step 2: Ensuring Artifact Registry exists..." -ForegroundColor Yellow
$repoExists = $false
try {
    gcloud artifacts repositories describe $ArtifactRepo --location=$Region --project=$ProjectId 2>$null
    if ($LASTEXITCODE -eq 0) { $repoExists = $true }
} catch {}

if (-not $repoExists) {
    gcloud artifacts repositories create $ArtifactRepo `
        --repository-format=docker `
        --location=$Region `
        --description="ZACMA Platform Docker Images" `
        --project=$ProjectId
    Write-Host "✅ Artifact Registry repository created." -ForegroundColor Green
} else {
    Write-Host "✅ Artifact Registry repository already exists." -ForegroundColor Green
}

# 3. Cloud Build
Write-Host "📦 Step 3: Submitting Cloud Build..." -ForegroundColor Yellow
$imageTag = "latest"
try { $imageTag = (git rev-parse --short HEAD 2>$null) } catch {}
if (-not $imageTag) { $imageTag = (Get-Date -Format "yyyyMMddHHmmss") }

gcloud builds submit `
    --config=cloudbuild.yaml `
    --substitutions=_TAG="$imageTag",_REGION="$Region",_REPO_NAME="$ArtifactRepo",_BACKEND_SERVICE="zacma-backend",_FRONTEND_SERVICE="zacma-frontend" `
    --project=$ProjectId

# 4. Results
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "🎉 DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan

$backendUrl = (gcloud run services describe zacma-backend --region=$Region --project=$ProjectId --format='value(status.url)')
$frontendUrl = (gcloud run services describe zacma-frontend --region=$Region --project=$ProjectId --format='value(status.url)')

Write-Host "🌐 Frontend URL: $frontendUrl" -ForegroundColor Cyan
Write-Host "🔌 Backend API:  $backendUrl" -ForegroundColor Cyan
Write-Host "📖 API Docs:     $backendUrl/docs" -ForegroundColor Cyan
Write-Host "🩺 Health Check: $backendUrl/health" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
