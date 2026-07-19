"""
Compiles the LangGraph state graph for AgriGuard AI.
Minimal linear graph: Supervisor → Executor → Reflection → END
"""
from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.nodes import supervisor_node, executor_node, reflection_node


def build_graph():
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("reflection", reflection_node)

    # Define edges
    workflow.set_entry_point("supervisor")
    workflow.add_edge("supervisor", "executor")
    workflow.add_edge("executor", "reflection")
    workflow.add_edge("reflection", END)

    return workflow.compile()


# Build the graph once
agent_graph = build_graph()