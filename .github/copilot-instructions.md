# GitHub Copilot Instructions for ZACMA Group

**Purpose**: Quick reference for Copilot to assist developers efficiently in the ZACMA platform.

---

## Quick Context

This is a **multi-tenant AI SaaS platform** built with:
- **Backend**: FastAPI + Supabase + LangChain/LangGraph agents
- **Frontend**: Next.js dashboard + Flutter mobile
- **AI Layer**: LangChain agents with RAG (Qdrant vector DB) and OmniRoute LLM gateway
- **Infrastructure**: Docker (Redis, Qdrant, n8n, OmniRoute, Prometheus, Grafana)

**Key Feature**: Tenant-aware architecture with Row-Level Security for multi-tenant isolation.

---

## Before Any Implementation

When asked to implement a feature or fix:

1. **Ask about tenant scope**: Does this affect single tenant or all tenants?
2. **Check module boundaries**: Is this a new domain module or an existing one?
3. **Verify auth/security**: Does this operation need tenant isolation?
4. **Confirm data flow**: Does this involve AI agents, database queries, or external API calls?

---

## Common Patterns to Follow

### Adding a New Module
```python
# backend/app/modules/{domain}/router.py
from fastapi import APIRouter, Depends
from app.core.tenancy import get_tenant_id

router = APIRouter(prefix="/{domain}", tags=["{domain}"])

@router.get("/")
async def list_{domain}(tenant_id: str = Depends(get_tenant_id)):
    # Query tenant-scoped data
    return {"domain": "{domain}", "tenant": tenant_id}
```

### Creating an AI Tool
```python
# ai/tools/registry.py
from langchain_core.tools import tool

@tool
def my_tool(query: str, tenant_id: str) -> str:
    """Tool description. Used as LLM instruction."""
    # Always use tenant_id for data access
    results = vector_db.search(query, namespace=tenant_id)
    return format_results(results)
```

### Using the Tenant Dependency
```python
# Always inject tenant_id via Depends(get_tenant_id)
async def protected_endpoint(tenant_id: str = Depends(get_tenant_id)):
    # Now you have authenticated tenant context
    user_data = db.query(User).filter(User.tenant_id == tenant_id)
    return user_data
```

---

## Code Style & Conventions

### Python (Backend)
- **Async by default**: Use `async def` for all FastAPI endpoints and I/O operations
- **Pydantic validation**: Define request models with Pydantic `BaseModel`
- **Router organization**: One router file per module (`router.py`)
- **Imports**: Keep `app.core`, `app.modules` organized; avoid circular imports

### TypeScript (Dashboard)
- **Tailwind CSS**: Use utility classes, avoid custom CSS
- **React Hooks**: Use `useState`, `useEffect` for component logic
- **Async API calls**: Use `fetch` or axios with proper error handling
- **Type safety**: Always define TypeScript interfaces for API responses

### Python (AI Agents)
- **LangChain tools**: Use `@tool` decorator with clear docstrings
- **Tenant awareness**: Always pass `tenant_id` to tools
- **Logging**: Log tool invocations for audit trails
- **Error handling**: Wrap agent calls with try-catch for graceful failures

---

## Gotchas to Avoid

1. **❌ Forgetting tenant_id** → Always `Depends(get_tenant_id)` for protected routes
2. **❌ Hardcoding prompts** → Use `ChatPromptTemplate` for dynamic prompts
3. **❌ Direct LLM access** → Always use agents with tools for guardrails
4. **❌ Missing vector DB context** → Use RAG tools, don't rely on LLM hallucinations
5. **❌ Unlogged tool calls** → Always log agent invocations for cost and audit
6. **❌ Cross-tenant data access** → Every query must filter by tenant
7. **❌ Sync I/O in async context** → Use `await` with async database calls

---

## File Navigation

| Need | Look Here |
|------|-----------|
| Add new API endpoint | `backend/app/modules/{domain}/router.py` |
| Create AI agent | `ai/agents/{domain}_agent.py` |
| Define tool | `ai/tools/registry.py` |
| Dashboard page | `dashboard/app/dashboard/{domain}/page.tsx` |
| Configuration | `backend/app/core/config.py` |
| Database schema | Supabase console (via `backend/app/core/db.py`) |
| Infrastructure | `infrastructure/docker-compose.yml` |

---

## Testing & Verification

```bash
# Run backend tests
cd backend && pytest tests/ -v

# Test endpoint locally
curl -X GET http://localhost:8000/api/v1/crm/ -H "Authorization: Bearer <token>"

# Check Vector DB
curl http://localhost:6333/dashboard  # Qdrant UI

# Monitor logs
docker logs -f <container_name>
```

---

## LLM Model & Context

- **OmniRoute Gateway**: Routes requests to Ollama (local) or OpenRouter (cloud)
- **Default Model**: `qwen2.5-coder:7b` (local) or configured cloud model
- **Token limits**: Respect context window; summarize long documents
- **Cost tracking**: All LLM calls routed through OmniRoute for billing

---

## When to Ask for Human Input

Before implementing, ask the developer:
- **Module scope**: Is this a new module or extending existing?
- **Tenant handling**: Single or multi-tenant operation?
- **AI involvement**: Does this need an agent or tool?
- **Data persistence**: What's the data model?
- **Security requirements**: Any special access control?

---

## One-Liner Commands

```bash
# Start everything locally
cd infrastructure && docker compose up -d && cd ../backend && source .venv/bin/activate && uvicorn app.main:app --reload &

# View FastAPI docs
open http://localhost:8000/docs

# Check service health
curl http://localhost:8000/health

# Ingest documents for RAG
python3 ai/rag/ingest.py --collection {domain}_docs --path docs/{domain}/

# Run tests with coverage
pytest backend/tests/ --cov=backend/app --cov-report=html
```

---

**Remember**: Always prioritize **tenant isolation**, **security**, and **code maintainability** over quick shortcuts!
