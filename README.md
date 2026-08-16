# ZACMA Group AI Platform

A multi-tenant AI platform skeleton for CRM, HRM, payments, training, travel, and visa operations. This repository follows the phased project guide and provides the starting structure for the infrastructure, backend, AI layer, and frontends.

## Monorepo Structure

- `backend/` – FastAPI services and tenant-aware module routers
- `ai/` – OmniRoute gateway, RAG scripts, tool registry, and agent stubs
- `infrastructure/` – Docker Compose for Redis, Qdrant, n8n, OmniRoute, Prometheus, and Grafana
- `automation/` – n8n workflow JSON exports
- `mobile/` – Flutter app shell
- `dashboard/` – Next.js dashboard and marketing frontend shell
- `docs/` – supporting notes and reference documentation
- `.github/workflows/` – CI checks

## Prerequisites

- WSL2 Ubuntu environment
- Docker Desktop with WSL2 backend enabled
- Node.js LTS
- Python 3.11+
- Flutter
- Ollama and a local model such as `llama3.1`

## Local Setup

```bash
cd infrastructure
docker compose up -d

cd ../backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Security and SaaS Principles

- Keep tenant isolation explicit with Supabase Row-Level Security.
- Require human confirmation for irreversible AI actions.
- Add Redis-backed rate limiting and tool-call audit logs.
- Use environment-scoped secrets and avoid storing production secrets in the repo.

## Build Order

1. Provision infrastructure and shared schema.
2. Confirm the backend pattern with a single module (CRM).
3. Wire OmniRoute and RAG.
4. Add agents and graph workflows.
5. Build automation and dashboards.
6. Harden security, CI, and SaaS features.
