"""Fast, deterministic LangGraph nodes backed by free public/local tools.

The previous graph called an 8B model twice per request. Routing and synthesis
are deliberately lightweight so the farmer gets a useful answer even without a
running local model. Ollama with Llama 3.2 3B remains the recommended optional
local model for future conversational enhancement, with no API key required.
"""
from typing import Any, Dict

from langchain_core.messages import AIMessage, HumanMessage

from app.agents.state import AgentState
from app.rag.retriever import search_kb
from app.services.watson_discovery import query_discovery
from app.tools.crop_disease import diagnose
from app.tools.market import get_market_prices
from app.tools.sustainability import get_sustainability_advice
from app.tools.weather import get_weather, resolve_location


def supervisor_node(state: AgentState) -> Dict[str, Any]:
    """Choose specialists predictably and preserve explicit report selection."""
    if state.get("required_agents"):
        return {"required_agents": state["required_agents"]}

    query = (state["messages"][-1].content if state.get("messages") else "").lower()
    agents = ["weather"]
    if any(word in query for word in ("report", "full plan", "overview")):
        agents = ["weather", "crop_doctor", "market", "sustainability"]
    else:
        if any(word in query for word in ("pest", "disease", "yellow", "spot", "leaf", "wilt", "problem", "symptom")):
            agents.append("crop_doctor")
        if any(word in query for word in ("price", "market", "sell", "buyer", "profit")):
            agents.append("market")
        if any(word in query for word in ("soil", "water", "sustain", "organic", "climate", "rotation")):
            agents.append("sustainability")
    if len(agents) == 1 and state.get("problem"):
        agents.append("crop_doctor")
    return {"required_agents": agents}


def executor_node(state: AgentState) -> dict:
    """Run the selected specialists, using optional Discovery then local RAG."""
    agents = state.get("required_agents", [])
    updates: dict[str, Any] = {}
    crop = state.get("crop", "unknown")
    problem = state.get("problem", "") or (state["messages"][-1].content if state.get("messages") else "")

    if "weather" in agents:
        try:
            lat, lon = resolve_location(state.get("location", ""))
            updates["weather_data"] = get_weather(lat, lon)
        except Exception as exc:
            updates["weather_data"] = f"Weather lookup unavailable: {exc}"

    if "crop_doctor" in agents:
        query = f"{crop} problem: {problem}"
        updates["disease_data"] = query_discovery(query) or search_kb(query, top_k=2) or diagnose(crop, problem)

    if "market" in agents:
        updates["market_data"] = get_market_prices(crop)

    if "sustainability" in agents:
        query = f"sustainable practices for {crop}"
        updates["sustainability_data"] = query_discovery(query) or search_kb(query, top_k=2) or get_sustainability_advice(crop)

    if not updates:
        updates["messages"] = [AIMessage(content="No specialist agents were required for this query.")]
    return updates


def reflection_node(state: AgentState) -> Dict[str, Any]:
    """Create a compact action plan without a second, slow model call."""
    labels = (
        ("weather_data", "Weather outlook"),
        ("disease_data", "Crop health"),
        ("market_data", "Market signal"),
        ("sustainability_data", "Sustainable practice"),
    )
    sections = [f"**{label}**\n{state[key]}" for key, label in labels if state.get(key)]
    question = next((m.content for m in reversed(state.get("messages", [])) if isinstance(m, HumanMessage)), "")
    final = (
        f"Here is your AgriGuard action brief for **{state.get('crop', 'your crop').title()}** "
        f"in **{state.get('location', 'your location')}**.\n\n"
        f"**Your question:** {question}\n\n"
        + "\n\n".join(sections)
        + "\n\n**Next steps:** Inspect the field before treating, follow product labels and local guidance, "
          "and contact an agricultural extension officer if symptoms spread quickly."
    )
    return {"final_response": final}
