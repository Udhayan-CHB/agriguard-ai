"""
LangGraph node functions. Each node receives the state and returns an update.
We use IBM Granite via Ollama for reasoning nodes.
"""
import json
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_ollama import ChatOllama
from app.agents.state import AgentState
from app.core.config import settings
from app.tools.weather import get_weather
from app.tools.crop_disease import diagnose
from app.tools.market import get_market_prices
from app.tools.sustainability import get_sustainability_advice

# ─── LLM instance (reused) ──────────────────────
llm = ChatOllama(
    model=settings.OLLAMA_MODEL,
    base_url=settings.OLLAMA_BASE_URL,
    temperature=0.3,
)

# ─── Supervisor Node ────────────────────────────
def supervisor_node(state: AgentState) -> Dict[str, Any]:
    user_msg = state["messages"][-1].content if state["messages"] else ""
    prompt = f"""You are a supervisor in an agricultural AI assistant.
Given the user query and farm context, decide which specialist agents to activate.

Agents:
- weather: provides weather forecast
- crop_doctor: diagnoses crop problems and gives treatment advice
- market: gives market prices and selling opportunities
- sustainability: suggests eco-friendly farming practices

Rules:
- If the user asks for a full report or uses the word 'report', activate ALL agents.
- If the user mentions a crop problem, activate crop_doctor.
- If the user asks about prices or market, activate market.
- If the user asks about the environment or sustainability, activate sustainability.
- Weather can always be helpful, so activate it unless the query clearly doesn't need it.

User query: "{user_msg}"
Farm context: crop={state.get('crop')}, location={state.get('location')}

Return ONLY a JSON list of agent names, e.g., ["weather", "crop_doctor"]"""


# # ─── Planner Node ───────────────────────────────
# def planner_node(state: AgentState) -> Dict[str, Any]:
#     """
#     Based on required agents, build a plan and invoke them.
#     This node acts as a simple scheduler.
#     """
#     # We'll actually execute the specialists in the graph via conditional edges,
#     # but here we just record the plan.
#     return {}  # no state update needed; routing handled by graph edges


# # ─── Specialist Nodes ───────────────────────────
# def weather_node(state: AgentState) -> Dict[str, Any]:
#     loc = state.get("location", "0,0")
#     try:
#         lat, lon = map(float, loc.split(","))
#     except:
#         lat, lon = 40.7128, -74.0060  # default NYC
#     data = get_weather(lat, lon)
#     return {"weather_data": data}

# def crop_doctor_node(state: AgentState) -> Dict[str, Any]:
#     crop = state.get("crop", "unknown")
#     problem = state.get("problem", "") or state["messages"][-1].content
#     advice = diagnose(crop, problem)
#     return {"disease_data": advice}

# def market_node(state: AgentState) -> Dict[str, Any]:
#     crop = state.get("crop", "maize")
#     prices = get_market_prices(crop)
#     return {"market_data": prices}

# def sustainability_node(state: AgentState) -> Dict[str, Any]:
#     crop = state.get("crop", "unknown")
#     tips = get_sustainability_advice(crop)
#     return {"sustainability_data": tips}


# ─── Reflection Node ────────────────────────────
def reflection_node(state: AgentState) -> Dict[str, Any]:
    """
    Combine all specialist data and generate a coherent response using Granite.
    """
    parts = []
    if state.get("weather_data"):
        parts.append(f"### Weather\n{state['weather_data']}")
    if state.get("disease_data"):
        parts.append(f"### Crop Health\n{state['disease_data']}")
    if state.get("market_data"):
        parts.append(f"### Market\n{state['market_data']}")
    if state.get("sustainability_data"):
        parts.append(f"### Sustainability\n{state['sustainability_data']}")

    combined = "\n\n".join(parts)
    if not combined:
        combined = "No specialist data available."

    user_query = state["messages"][-1].content if state["messages"] else ""
    system_prompt = f"""You are a helpful agricultural assistant.
Based on the following expert information and the farmer's query, write a concise, actionable response.

Farmer query: "{user_query}"
Crop: {state.get('crop')}
Location: {state.get('location')}

Expert data:
{combined}

Write a final answer for the farmer. Be encouraging and practical."""
    
    response = llm.invoke([SystemMessage(content=system_prompt)])
    final = response.content.strip()
    return {"final_response": final}


# # ─── Memory Node ────────────────────────────────
# def memory_node(state: AgentState) -> Dict[str, Any]:
#     """
#     This node doesn't alter state; we'll store messages in the API endpoint.
#     (Here we just pass through.)
#     """
#     return {}

def executor_node(state: AgentState) -> dict:
    """Run all specialist tools that the supervisor requested."""
    agents = state.get("required_agents", [])
    updates = {}
    crop = state.get("crop", "unknown")
    problem = state.get("problem", "") or (
        state["messages"][-1].content if state["messages"] else ""
    )
    loc = state.get("location", "0,0")
    try:
        lat, lon = map(float, loc.split(","))
    except Exception:
        lat, lon = 40.7128, -74.0060

    if "weather" in agents:
        updates["weather_data"] = get_weather(lat, lon)
    if "crop_doctor" in agents:
        updates["disease_data"] = diagnose(crop, problem)
    if "market" in agents:
        updates["market_data"] = get_market_prices(crop)
    if "sustainability" in agents:
        updates["sustainability_data"] = get_sustainability_advice(crop)

    # Ensure we always return at least one state key
    if not updates:
        updates["messages"] = [AIMessage(content="No specialist agents were required for this query.")]
    
    return updates