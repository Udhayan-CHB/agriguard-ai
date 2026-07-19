"""
Defines the state object that flows through the LangGraph agent graph.
"""
from typing import TypedDict, List, Optional, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    # The conversation messages (history)
    messages: Annotated[List[BaseMessage], add_messages]

    # Farm profile info
    farm_id: Optional[int]
    username: Optional[str]
    location: str           # "lat,lng"
    crop: str
    farm_size_hectares: float
    problem: str            # user's problem description

    # Agent execution plan
    required_agents: List[str]   # e.g. ["weather", "crop_doctor"]

    # Collected results from specialists
    weather_data: Optional[str]
    disease_data: Optional[str]
    market_data: Optional[str]
    sustainability_data: Optional[str]

    # Final output
    final_response: Optional[str]