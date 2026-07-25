"""Deterministic agent nodes for AgriGuard AI.

The advisory service must remain usable when a local LLM is unavailable, so
tool selection and response assembly deliberately do not depend on Ollama.
"""
from typing import Any, Dict

from langchain_core.messages import AIMessage

from app.agents.state import AgentState
from app.services.watson_discovery import query_discovery
from app.tools.crop_disease import diagnose
from app.tools.market import get_market_prices
from app.tools.sustainability import get_sustainability_advice
from app.tools.weather import get_weather, resolve_location


KNOWN_CROPS = ("maize", "rice", "wheat", "soybean")

CROP_OVERVIEWS = {
    "maize": (
        "Maize grows best in well-drained soil with good sunlight. Keep moisture steady, "
        "use split nitrogen applications, control weeds early, and inspect leaves weekly for pests and disease."
    ),
    "rice": (
        "Rice benefits from level fields, careful water management, split nitrogen applications, "
        "and regular checks for leaf spots, borers, and uneven yellowing."
    ),
    "wheat": (
        "Wheat needs timely sowing, balanced nitrogen, good drainage, and regular monitoring for rust and aphids."
    ),
    "soybean": (
        "Soybean benefits from well-drained soil, early weed control, and monitoring for leaf-feeding insects and disease."
    ),
}


def _crop_from_messages(state: AgentState) -> str:
    """Use a crop named in the current conversation when no profile crop is active."""
    profile_crop = str(state.get("crop", "unknown")).lower().strip()
    if profile_crop in KNOWN_CROPS:
        return profile_crop
    for message in reversed(state.get("messages", [])):
        text = str(message.content).lower()
        for crop in KNOWN_CROPS:
            if crop in text:
                return crop
    return "unknown"


def _select_agents(message: str) -> list[str]:
    """Select applicable specialist tools from clear user-request keywords."""
    query = message.lower()
    if "report" in query:
        return ["weather", "crop_doctor", "market", "sustainability"]

    agents: list[str] = []
    if any(word in query for word in ("weather", "rain", "temperature", "forecast", "wind", "humidity")):
        agents.append("weather")
    if any(word in query for word in (
        "disease", "pest", "insect", "yellow", "yellowing", "spot", "spots",
        "leaf", "leaves", "rust", "blight", "wilt", "stunted", "growth", "yield", "yeild",
    )):
        agents.append("crop_doctor")
    if any(crop in query for crop in KNOWN_CROPS) and not agents:
        agents.append("crop_info")
    if any(word in query for word in ("price", "prices", "market", "sell", "selling", "buyer")):
        agents.append("market")
    if any(word in query for word in ("sustainable", "sustainability", "organic", "eco", "water saving", "soil health")):
        agents.append("sustainability")
    return agents


def supervisor_node(state: AgentState) -> Dict[str, Any]:
    user_msg = state["messages"][-1].content if state["messages"] else ""
    # Reports preselect all specialists. Keep that explicit selection intact.
    return {
        "crop": _crop_from_messages(state),
        "required_agents": state.get("required_agents") or _select_agents(user_msg),
    }


def executor_node(state: AgentState) -> dict:
    """Run the selected local or public-data specialists."""
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
        updates["disease_data"] = query_discovery(query) or diagnose(crop, problem)
    if "crop_info" in agents:
        updates["crop_info"] = CROP_OVERVIEWS[crop]
    if "market" in agents:
        updates["market_data"] = get_market_prices(crop)
    if "sustainability" in agents:
        updates["sustainability_data"] = query_discovery(f"sustainable practices for {crop}") or get_sustainability_advice(crop)
    if not updates:
        updates["messages"] = [AIMessage(content="No specialist agents were required for this query.")]
    return updates


def reflection_node(state: AgentState) -> Dict[str, Any]:
    """Turn specialist results into a clear response without an LLM call."""
    sections = []
    for title, key in (
        ("Weather", "weather_data"),
        ("Crop Health", "disease_data"),
        ("Market", "market_data"),
        ("Sustainability", "sustainability_data"),
        ("Crop Guide", "crop_info"),
    ):
        if state.get(key):
            sections.append(f"{title}:\n{state[key]}")

    if sections:
        final = "Here is the advisory information I found:\n\n" + "\n\n".join(sections)
        final += "\n\nUse products only as directed on their labels, and contact a local agricultural officer if symptoms spread quickly."
    else:
        final = (
            "I can help with crop problems, weather, market prices, and sustainable farming. "
            "Tell me the crop, location, and what you are observing (such as yellow leaves, spots, pests, or poor growth) for specific advice."
        )
    return {"final_response": final}
