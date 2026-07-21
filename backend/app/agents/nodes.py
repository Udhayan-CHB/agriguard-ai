"""Fast, deterministic LangGraph nodes backed by free public/local tools.

The previous graph called an 8B model twice per request. Routing and synthesis
are deliberately lightweight so the farmer gets a useful answer even without a
running local model. Ollama with Llama 3.2 3B remains the recommended optional
local model for future conversational enhancement, with no API key required.
"""
from typing import Any, Dict

from langchain_core.messages import AIMessage, HumanMessage

from app.agents.state import AgentState
from app.services.watson_discovery import query_discovery
from app.tools.crop_disease import diagnose
from app.tools.market import get_market_prices
from app.tools.sustainability import get_sustainability_advice
from app.tools.weather import get_weather, resolve_location


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
- If the user is just greeting, asking about your capabilities, or making small talk, return an empty list [].
- If the user asks for a full report or uses the word 'report', activate ALL agents.
- If the user mentions a specific crop problem (like "yellow leaves", "pests"), activate crop_doctor.
- If the user asks about prices or market, activate market.
- If the user asks about sustainability or eco-friendly practices, activate sustainability.
- Weather can be helpful when the query is about rain, temperature, or location-specific conditions.

User query: "{user_msg}"
Farm context: crop={state.get('crop')}, location={state.get('location')}

Return ONLY a JSON list of agent names, e.g., ["weather", "crop_doctor"]. If no agents needed, return []."""

    system_msg = SystemMessage(content=prompt)
    response = llm.invoke([system_msg])
    content = response.content.strip()
    try:
        agents = json.loads(content)
        if not isinstance(agents, list):
            agents = []
    except:
        agents = []
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
        # The curated adviser is instant and offline. Discovery is retained as
        # an optional enrichment only when the user has configured it. Do not
        # initialize a large embedding model in the critical chat path.
        updates["disease_data"] = query_discovery(query) or diagnose(crop, problem)

    if "market" in agents:
        updates["market_data"] = get_market_prices(crop)

    if "sustainability" in agents:
        query = f"sustainable practices for {crop}"
        updates["sustainability_data"] = query_discovery(query) or get_sustainability_advice(crop)

    if not updates:
        updates["messages"] = [AIMessage(content="No specialist agents were required for this query.")]
    return updates


def reflection_node(state: AgentState) -> Dict[str, Any]:
    # Gather specialist data if any
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

    # Build conversation history
    history_str = ""
    messages = state.get("messages", [])
    if len(messages) > 1:
        last_msgs = messages[-4:]
        for msg in last_msgs:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            content = msg.content[:300]
            history_str += f"{role}: {content}\n"

    # Current user question
    current_question = ""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            current_question = msg.content
            break

    # Choose system prompt based on whether we have specialist data
    if combined:
        system_prompt = f"""You are a helpful agricultural assistant.
Refer to the conversation history to give consistent, contextual advice.

Conversation history:
{history_str if history_str else "No prior conversation."}

Current question: "{current_question}"
Crop: {state.get('crop')}
Location: {state.get('location')}

Expert data gathered from tools:
{combined}

Write a final, friendly answer. Use bullet points if needed. Be encouraging and practical."""
    else:
        # No specialist data – act as a general assistant
        system_prompt = f"""You are AgriGuard, a friendly AI assistant for farmers. 
You can help with crop problems, weather, market prices, and sustainable farming.
If the user greets you or asks about your capabilities, respond warmly and briefly explain what you can do.
If the query is unrelated to farming, politely steer them back to agricultural topics.

Conversation history:
{history_str if history_str else "No prior conversation."}

Current question: "{current_question}"

Write a helpful, concise response."""

    response = llm.invoke([SystemMessage(content=system_prompt)])
    final = response.content.strip()
    return {"final_response": final}