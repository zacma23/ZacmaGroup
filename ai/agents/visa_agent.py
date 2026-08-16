from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

from ai.llm import build_chat_model
from ai.tools.registry import search_documents

llm = build_chat_model()


@tool
def visa_docs_search(query: str, tenant_id: str) -> str:
    """Search visa requirement documents for this tenant."""
    results = search_documents(tenant_id=tenant_id, query=query, collection="visa_docs")
    return "\n---\n".join(results)


prompt = ChatPromptTemplate.from_messages([
    ("system", "You are the ZACMA Visa Assistant. Answer only using retrieved documents. If information isn't found, say so and offer to escalate."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, [visa_docs_search], prompt)
visa_agent_executor = AgentExecutor(agent=agent, tools=[visa_docs_search], verbose=True)
