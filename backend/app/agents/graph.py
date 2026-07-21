"""
Compiles the LangGraph state graph for AgriGuard AI.
Minimal linear graph: Supervisor → Executor → Reflection → END
"""
from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.nodes import supervisor_node, executor_node, reflection_node


def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("reflection", reflection_node)

    workflow.set_entry_point("supervisor")

    # Conditional edge: if no agents required, go straight to reflection
    def route_after_supervisor(state: AgentState) -> str:
        if state.get("required_agents"):
            return "executor"
        return "reflection"

    workflow.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {
            "executor": "executor",
            "reflection": "reflection",
        }
    )

    workflow.add_edge("executor", "reflection")
    workflow.add_edge("reflection", END)

    return workflow.compile()

# Build the graph once
agent_graph = build_graph()