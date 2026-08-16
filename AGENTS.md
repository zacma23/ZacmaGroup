# ZACMA Group AI Agent Guide

**Purpose**: Help AI coding agents become immediately productive in the ZACMA platform monorepo by understanding architecture, conventions, and development workflows.

**Project**: Multi-tenant AI-powered SaaS platform for CRM, HRM, payments, training, travel, and visa operations.

---

## 🏗️ Architecture Overview

### High-Level Topology
```
Internet → Caddy (Reverse Proxy)
         ├→ Next.js Dashboard + Frontend
         ├→ FastAPI Backend API
         └→ Supabase (Auth + DB)
              ├→ Redis (Caching, Rate Limiting)
              ├→ Qdrant (Vector DB for RAG)
              └→ OmniRoute → Ollama (Local LLM) / OpenRouter (Cloud LLM)
```

### Repository Structure

| Directory | Purpose |
|-----------|---------|
| `backend/` | FastAPI services with modular tenant-aware routers |
| `ai/` | LangChain agents, LangGraph workflows, RAG pipeline, tool registry |
| `dashboard/` | Next.js UI (admin dashboards, module interfaces) |
| `mobile/` | Flutter app shell for mobile clients |
| `infrastructure/` | Docker Compose (Redis, Qdrant, n8n, OmniRoute, Prometheus, Grafana) |
| `automation/` | n8n workflow exports for business process automation |
| `docs/` | Supporting architecture and reference documentation |

---

## 🔧 Tech Stack & Dependencies

### Backend
- **Framework**: FastAPI 0.111.0 with Uvicorn
- **Authentication**: Supabase (Row-Level Security for tenant isolation)
- **AI/ML**: LangChain 0.3.27, LangGraph 0.5.0, Sentence Transformers 3.4.1
- **Vector DB**: Qdrant Client 1.14.2 (for RAG)
- **Caching**: Redis
- **Testing**: pytest, pytest-asyncio
- **Data**: Pydantic for validation, python-dotenv for config

### Frontend
- **Framework**: Next.js with TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Context (see `components/PreviewProvider.tsx`, `SidebarProvider.tsx`)

### Mobile
- **Framework**: Flutter (Dart)

### Infrastructure
- **Containerization**: Docker Compose
- **Monitoring**: Prometheus + Grafana
- **Workflow Automation**: n8n
- **LLM Gateway**: OmniRoute (routes to Ollama locally or OpenRouter cloud)

---

## 🎯 Key Architectural Patterns

### 1. **Modular Backend Architecture**

**Pattern**: Each business domain (CRM, HRM, Payments, etc.) is a module with its own router.

```python
# backend/app/modules/{domain}/router.py
from fastapi import APIRouter
router = APIRouter(prefix="/{domain}", tags=["{domain}"])

# Then included in main.py:
app.include_router(router, prefix="/api/v1")
```

**Conventions**:
- One router file per module (`router.py`)
- Routers mounted at `GET /api/v1/{domain}/*`
- Domain logic stays isolated within its module directory
- No cross-module imports; use shared utilities from `app/core/`

**When Adding a New Module**:
1. Create `backend/app/modules/{domain}/` directory
2. Implement `router.py` with FastAPI router
3. Include router in `backend/app/main.py` with `app.include_router()`
4. Wire up Dashboard pages in `dashboard/app/dashboard/{domain}/`

---

### 2. **Multi-Tenancy & Tenant Isolation**

**Pattern**: Tenant ID is extracted from authenticated user context; used as a request dependency.

```python
# backend/app/core/tenancy.py
def get_tenant_id(request: Request) -> str:
    """Extract tenant from request.state.user or use demo tenant."""
    user = getattr(request.state, "user", None)
    if isinstance(user, Mapping):
        tenant_id = user.get("tenant_id")
        if isinstance(tenant_id, str) and tenant_id.strip():
            return tenant_id
    if settings.demo_mode:
        return settings.demo_tenant_id
    raise HTTPException(status_code=401, detail="Authentication required")
```

**Principles**:
- **No tenant selection via headers or payload** – authentication alone determines tenant
- **Row-Level Security (RLS)** – Supabase enforces tenant boundaries at DB layer
- **Demo Mode** – Local dev uses `settings.demo_tenant_id = "zacma-demo"`
- **Never bypass tenant isolation** – always pass `tenant_id` to data access and AI tools

**When Accessing Data**:
```python
# ✅ Correct: pass tenant_id to database operations
results = search_documents(tenant_id=tenant_id, query=query, collection="visa_docs")

# ❌ Wrong: operate without tenant context
results = search_documents(query=query)  # Missing tenant isolation!
```

---

### 3. **AI Agents with Tool Calling & RAG**

**Pattern**: LangChain agents with tool registry and vector DB retrieval.

```python
# ai/agents/visa_agent.py
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.tools import tool
from ai.llm import build_chat_model

llm = build_chat_model()  # Routes to OmniRoute gateway

@tool
def visa_docs_search(query: str, tenant_id: str) -> str:
    """Search visa requirement documents for this tenant."""
    results = search_documents(tenant_id=tenant_id, query=query, collection="visa_docs")
    return "\n---\n".join(results)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are the ZACMA Visa Assistant. Answer only using retrieved documents."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, [visa_docs_search], prompt)
visa_agent_executor = AgentExecutor(agent=agent, tools=[visa_docs_search], verbose=True)
```

**Endpoint**:
```python
@router.post("/ai/chat/{agent_name}")
def chat(agent_name: str, payload: dict, tenant_id: str = Depends(get_tenant_id)):
    agent = AGENTS.get(agent_name)
    if not agent:
        return {"error": "unknown agent"}
    result = agent.invoke({"input": payload.get("message", ""), "tenant_id": tenant_id})
    return {"response": result.get("output", "")}
```

**Principles**:
- **Always include tenant_id** in tool invocations and vector DB queries
- **Define custom tools with @tool decorator** and docstrings (LLM uses these as instructions)
- **Use RAG for domain knowledge** – embed docs in Qdrant, retrieve in tools
- **Require human confirmation** for irreversible actions (e.g., visa approvals, payments)
- **Log all tool calls** for audit trails and cost tracking

**When Creating a New Agent**:
1. Create `ai/agents/{domain}_agent.py`
2. Import `build_chat_model()` from `ai/llm.py`
3. Register tools in `ai/tools/registry.py`
4. Define custom `@tool` functions with tenant_id parameter
5. Expose via endpoint in `backend/app/gateway.py`

---

### 4. **Configuration Management**

**Pattern**: Environment-driven settings with demo mode fallbacks for local development.

```python
# backend/app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_environment: str = "development"
    demo_mode: bool = True
    demo_tenant_id: str = "zacma-demo"
    
    supabase_url: str = "http://localhost:54321"
    supabase_service_key: str = ""
    omniroute_url: str = "http://localhost:20128/v1"
    ollama_base_url: str = "http://localhost:11434/v1"
    redis_url: str = "redis://localhost:6379"
    
    model_config = SettingsConfigDict(
        env_file=(BACKEND_DIR / ".env", REPOSITORY_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

settings = Settings()
```

**Conventions**:
- Env files: `.env` in repo root and `backend/.env` (git-ignored)
- **Never commit secrets** – use environment variables
- **Demo mode=true** for local dev (uses mock tenant, local Ollama)
- **Demo mode=false** in production (requires Supabase credentials, OpenRouter API keys)

---

## 🚀 Development Workflow

### Local Setup

```bash
# 1. Start infrastructure (Redis, Qdrant, OmniRoute, etc.)
cd infrastructure
docker compose up -d

# 2. Verify Ollama is running
ollama serve  # (separate terminal) Downloads llama3.1 on first run

# 3. Start Backend API
cd backend
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 4. Start Dashboard (another terminal)
cd dashboard
npm install
npm run dev  # Runs on http://localhost:3001

# 5. Start Mobile (Flutter)
cd mobile
flutter run
```

**Key URLs**:
- Backend API: `http://localhost:8000`
- Backend Docs: `http://localhost:8000/docs`
- Dashboard: `http://localhost:3001`
- Qdrant Vector DB UI: `http://localhost:6333/dashboard`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`

### Running Tests

```bash
cd backend
pytest tests/ -v
pytest tests/test_crm.py -v  # Single module test
```

### Adding New AI Features

1. **Ingest Documents** (RAG):
   ```bash
   python3 ai/rag/ingest.py --collection visa_docs --path docs/visa/
   ```

2. **Create Tool**:
   ```python
   # ai/tools/registry.py
   @tool
   def new_tool(query: str, tenant_id: str) -> str:
       """Tool description used by LLM."""
       pass
   ```

3. **Wire Agent**:
   - Create `ai/agents/{domain}_agent.py`
   - Expose via `backend/app/gateway.py` → `POST /ai/chat/{agent_name}`

4. **Dashboard Integration**:
   - Create React component in `dashboard/app/dashboard/{domain}/`
   - Connect to backend endpoint

---

## 🔒 Security & SaaS Principles

### Critical Rules

1. **Tenant Isolation**
   - ✅ Always depend on `get_tenant_id()` for request-level tenant context
   - ✅ Pass `tenant_id` to all data access and AI operations
   - ❌ Never allow caller to specify tenant in headers or payload
   - ❌ Never skip row-level security checks

2. **AI Agent Safety**
   - ✅ Log all tool invocations for audit trails
   - ✅ Require human approval for irreversible actions (transfers, approvals, etc.)
   - ✅ Rate limit agent endpoints (Redis-backed)
   - ❌ Do NOT expose raw LLM access without guardrails

3. **Secrets Management**
   - ✅ Store in environment variables
   - ✅ Use `.env` files locally (git-ignored)
   - ✅ Rotate OpenRouter/OmniRoute keys in production
   - ❌ Never commit API keys, DB credentials, or service role keys

4. **Cost Control**
   - ✅ Track AI token usage (via OmniRoute proxy)
   - ✅ Monitor per-tenant agent costs in Grafana
   - ✅ Set rate limits and quota per tenant
   - ❌ Do NOT enable unlimited LLM calls

---

## 📊 Monitoring & Observability

**Grafana Dashboards** (running at `http://localhost:3000`):
- Revenue per tenant
- Active tenant count
- AI cost per conversation
- Agent quality metrics (accuracy, latency)
- Error rates and uptime

**Prometheus Metrics**:
- Endpoint latency (FastAPI automatic)
- Tool invocation counts
- Vector DB query times
- Agent execution duration

**Audit Logs**:
- All tool calls logged with tenant_id, user, timestamp, input, output
- Used for cost tracking, debugging, compliance

---

## 🛠️ Common Development Tasks

### Add a New Module (e.g., Logistics)

```bash
# 1. Backend router
backend/app/modules/logistics/router.py
# → Define endpoints for shipment tracking, etc.

# 2. Include in main.py
# → Add: app.include_router(logistics_router, prefix="/api/v1")

# 3. Dashboard page
dashboard/app/dashboard/logistics/page.tsx
# → React component for logistics dashboard

# 4. Mobile feature (optional)
mobile/lib/features/logistics/
# → Flutter screens
```

### Create an AI Agent for a New Domain

```bash
# 1. ai/agents/logistics_agent.py
# → Define tools and prompt

# 2. ai/tools/registry.py
# → Add logistics-specific tools (search_shipments, etc.)

# 3. backend/app/gateway.py
# → Wire agent endpoint

# 4. dashboard/app/api/chat/route.ts (or equivalent)
# → Frontend endpoint to call agent

# 5. Ingest docs
python3 ai/rag/ingest.py --collection logistics_docs --path docs/logistics/
```

### Implement Row-Level Security (RLS) Policy

```sql
-- Supabase SQL editor
CREATE POLICY "tenant_isolation" ON crm_contacts
  USING (tenant_id = auth.jwt() ->> 'tenant_id');
```

---

## ⚠️ Common Pitfalls & Gotchas

| Issue | Solution |
|-------|----------|
| **Missing tenant_id in data queries** | Always use `Depends(get_tenant_id)` and pass to DB calls |
| **Hardcoded LLM prompts** | Use `ChatPromptTemplate` and parameterize system messages |
| **Skipping vector DB queries** | Use RAG tools for domain knowledge; avoid hallucination |
| **Exposing raw agent responses** | Log and validate outputs before returning to frontend |
| **Not handling auth failures** | `get_tenant_id()` raises HTTPException(401) on missing auth |
| **Docker not running** | `docker compose up -d` in `infrastructure/`; check `docker ps` |
| **Ollama model not cached** | First run downloads ~7GB; use `ollama pull qwen2.5-coder:7b` |
| **Stale vector embeddings** | Re-ingest docs after updating `.txt` files in `docs/` |
| **Agent verbosity overload** | Set `verbose=False` in `AgentExecutor` for production |

---

## 📚 Key Files to Know

| File | Purpose |
|------|---------|
| `backend/app/main.py` | FastAPI app, router registration |
| `backend/app/core/config.py` | Settings, environment variables |
| `backend/app/core/tenancy.py` | Tenant extraction, multi-tenancy |
| `backend/app/gateway.py` | AI agent endpoints |
| `ai/llm.py` | LLM initialization (OmniRoute integration) |
| `ai/agents/{domain}_agent.py` | Agent definitions |
| `ai/tools/registry.py` | Tool implementations |
| `ai/rag/ingest.py` | Document ingestion for RAG |
| `dashboard/components/PreviewProvider.tsx` | Frontend preview/tenant context |
| `infrastructure/docker-compose.yml` | Container definitions |

---

## 🎓 Agent Recommendations

### Before Any Code Change
1. ✅ Understand the module/domain context
2. ✅ Check tenant isolation implications
3. ✅ Review security rules above
4. ✅ Confirm local setup is running (`docker ps`, `curl http://localhost:8000/health`)

### For Backend Changes
- Follow FastAPI async patterns (`async def` for I/O-bound operations)
- Use Pydantic models for request/response validation
- Always return tenant-scoped results
- Write tests in `backend/tests/`

### For AI/Agent Changes
- Use `@tool` decorators with clear docstrings
- Always include `tenant_id` parameter
- Log tool invocations for audit trails
- Test RAG retrieval accuracy before deployment

### For Frontend Changes
- Use Tailwind CSS utilities (avoid custom CSS)
- Leverage `PreviewProvider` for tenant context
- Test auth flows (login → tenant selection → dashboard)

---

## 📖 References

- [README.md](README.md) – Project overview and setup instructions
- [docs/build-guide-summary.md](docs/build-guide-summary.md) – Production topology and monitoring
- [infrastructure/docker-compose.yml](infrastructure/docker-compose.yml) – Service definitions
- FastAPI Docs: https://fastapi.tiangolo.com/
- LangChain Docs: https://python.langchain.com/
- Next.js Docs: https://nextjs.org/docs
- Supabase RLS: https://supabase.com/docs/guides/auth/row-level-security

---

**Last Updated**: 2026-08-16  
**Maintained By**: AI Agent Development Team
