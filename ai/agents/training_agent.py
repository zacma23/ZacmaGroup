from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

from ai.llm import build_chat_model
from ai.tools.registry import search_documents

llm = build_chat_model()


def make_training_agent():
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are the ZACMA training assistant. Answer with only tenant-scoped course data."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    agent = create_tool_calling_agent(llm, [search_documents], prompt)
    return AgentExecutor(agent=agent, tools=[search_documents], verbose=True)


training_agent_executor = make_training_agent()
