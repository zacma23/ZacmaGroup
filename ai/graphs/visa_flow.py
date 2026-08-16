from langgraph.graph import END, StateGraph


class VisaState(dict):
    tenant_id: str
    documents: list
    missing: list
    submitted: bool


def check_documents(state: dict) -> dict:
    required = {"passport", "photo", "application_form"}
    provided = {item.get("type") for item in state.get("documents", [])}
    state["missing"] = sorted(required - provided)
    return state


def request_missing(state: dict) -> dict:
    state["missing"] = state.get("missing", [])
    return state


def submit_application(state: dict) -> dict:
    state["submitted"] = True
    return state


def route(state: dict) -> str:
    return "request_missing" if state.get("missing") else "submit_application"


graph = StateGraph(dict)
graph.add_node("check_documents", check_documents)
graph.add_node("request_missing", request_missing)
graph.add_node("submit_application", submit_application)
graph.set_entry_point("check_documents")
graph.add_conditional_edges("check_documents", route, {
    "request_missing": "request_missing",
    "submit_application": "submit_application",
})
graph.add_edge("request_missing", END)
graph.add_edge("submit_application", END)

visa_flow = graph.compile()
