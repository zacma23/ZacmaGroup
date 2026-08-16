from fastapi import APIRouter, Depends

from app.core.tenancy import get_tenant_id
from ai.agents.visa_agent import visa_agent_executor
from ai.agents.training_agent import training_agent_executor

router = APIRouter(prefix="/ai", tags=["ai"])
AGENTS = {
    "visa": visa_agent_executor,
    "training": training_agent_executor,
}


@router.post("/chat/{agent_name}")
def chat(agent_name: str, payload: dict, tenant_id: str = Depends(get_tenant_id)):
    agent = AGENTS.get(agent_name)
    if not agent:
        return {"error": "unknown agent"}
    result = agent.invoke({"input": payload.get("message", ""), "tenant_id": tenant_id})
    return {"response": result.get("output", "")}
