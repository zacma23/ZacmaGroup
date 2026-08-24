"""AI agent gateway — exposes chat endpoints for domain-specific AI agents.

Mounts at ``/api/v1/ai`` and provides ``POST /chat/{agent_name}`` for invoking
registered agents. Includes a ``general`` fallback agent for general queries.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.tenancy import get_tenant_id

logger = logging.getLogger("zacma.ai")

router = APIRouter(prefix="/ai", tags=["ai"])

# Build agent executors — these may fail if LLM is not available
AGENTS: dict = {}

try:
    from ai.agents.visa_agent import visa_agent_executor
    AGENTS["visa"] = visa_agent_executor
except Exception as e:
    logger.warning("Visa agent not available: %s", e)

try:
    from ai.agents.training_agent import training_agent_executor
    AGENTS["training"] = training_agent_executor
except Exception as e:
    logger.warning("Training agent not available: %s", e)


@router.post("/chat/{agent_name}")
def chat(agent_name: str, payload: dict, tenant_id: str = Depends(get_tenant_id)):
    """Invoke a named AI agent with a chat message.

    The ``general`` agent name is a catch-all that uses whatever agent is
    available, or returns a helpful message if no agents are loaded.
    """
    # Handle "general" by trying any available agent
    if agent_name == "general":
        if not AGENTS:
            return {
                "response": (
                    "AI agents are not currently available. "
                    "Please ensure Ollama is running and the required models are installed. "
                    "Run: ollama pull qwen2.5-coder:7b"
                )
            }
        # Use first available agent for general queries
        agent = next(iter(AGENTS.values()))
    else:
        agent = AGENTS.get(agent_name)

    if not agent:
        available = list(AGENTS.keys()) + ["general"]
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown agent '{agent_name}'. Available agents: {available}",
        )

    try:
        result = agent.invoke({
            "input": payload.get("message", ""),
            "tenant_id": tenant_id,
        })
        return {"response": result.get("output", "")}
    except Exception as e:
        logger.error("Agent '%s' failed: %s", agent_name, e)
        return {
            "response": (
                "I'm sorry, I couldn't process that request right now. "
                "The AI service may be temporarily unavailable. "
                "Please try again later."
            )
        }


@router.get("/agents")
def list_agents():
    """List all available AI agents."""
    return {
        "agents": list(AGENTS.keys()) + ["general"],
        "count": len(AGENTS) + 1,
    }
