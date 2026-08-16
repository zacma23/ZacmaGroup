# Build guide summary

## Production topology

Internet -> Caddy -> Next.js dashboard + FastAPI API
-> Supabase + Redis + Qdrant
-> OmniRoute -> Ollama + OpenRouter

## Keep the business plan alive

Use Grafana dashboards for revenue, active tenants, AI cost per conversation, and agent quality metrics.
