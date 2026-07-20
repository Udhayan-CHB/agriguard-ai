from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import Conversation, Message, User, FarmProfile
from app.schemas.chat import ChatRequest, ChatResponse
from app.agents.graph import agent_graph
from langchain_core.messages import HumanMessage, AIMessage
from fastapi.responses import StreamingResponse
import asyncio

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ChatResponse)
def chat_with_agent(request: ChatRequest, db: Session = Depends(get_db)):
    # Validate user and farm profile
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    farm = db.query(FarmProfile).filter(
        FarmProfile.id == request.farm_profile_id,
        FarmProfile.user_id == user.id
    ).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm profile not found")

    # Retrieve conversation history
    conversation = db.query(Conversation).filter(
        Conversation.user_id == user.id,
        Conversation.farm_profile_id == farm.id
    ).first()
    if not conversation:
        conversation = Conversation(user_id=user.id, farm_profile_id=farm.id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Build message history for LangGraph
    previous_messages = []
    for msg in conversation.messages:
        if msg.role == "user":
            previous_messages.append(HumanMessage(content=msg.content))
        else:
            previous_messages.append(AIMessage(content=msg.content))

    # Add the new user message
    new_user_msg = HumanMessage(content=request.message)
    all_messages = previous_messages + [new_user_msg]

    # Prepare initial state for graph
    initial_state = {
        "messages": all_messages,
        "farm_id": farm.id,
        "username": request.username,
        "location": farm.location,
        "crop": farm.crop,
        "farm_size_hectares": farm.farm_size_hectares,
        "problem": farm.problem or request.message,
    }

    # Run the agent graph
    result = agent_graph.invoke(initial_state)

    final_response = result.get("final_response", "I'm sorry, I couldn't process your request.")

    # Save messages to DB
    user_msg_db = Message(conversation_id=conversation.id, role="user", content=request.message)
    db.add(user_msg_db)
    assistant_msg_db = Message(conversation_id=conversation.id, role="assistant", content=final_response)
    db.add(assistant_msg_db)
    db.commit()

    return ChatResponse(reply=final_response, agent_path="Supervisor → Executor → Reflection")

@router.post("/stream")
async def chat_stream(request: ChatRequest, db: Session = Depends(get_db)):
    """Stream the AI reply token by token (Server-Sent Events)."""
    # Validate user and farm profile (same as before)
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    farm = db.query(FarmProfile).filter(
        FarmProfile.id == request.farm_profile_id,
        FarmProfile.user_id == user.id
    ).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm profile not found")

    conversation = db.query(Conversation).filter(
        Conversation.user_id == user.id,
        Conversation.farm_profile_id == farm.id
    ).first()
    if not conversation:
        conversation = Conversation(user_id=user.id, farm_profile_id=farm.id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Build message history
    previous_messages = []
    for msg in conversation.messages:
        if msg.role == "user":
            previous_messages.append(HumanMessage(content=msg.content))
        else:
            previous_messages.append(AIMessage(content=msg.content))

    new_user_msg = HumanMessage(content=request.message)
    all_messages = previous_messages + [new_user_msg]

    initial_state = {
        "messages": all_messages,
        "farm_id": farm.id,
        "username": request.username,
        "location": farm.location,
        "crop": farm.crop,
        "farm_size_hectares": farm.farm_size_hectares,
        "problem": farm.problem or request.message,
    }

    # Run the graph up to the reflection node to get the final state
    result = agent_graph.invoke(initial_state)
    final_text = result.get("final_response", "")

    # Save messages to DB
    user_msg_db = Message(conversation_id=conversation.id, role="user", content=request.message)
    db.add(user_msg_db)
    assistant_msg_db = Message(conversation_id=conversation.id, role="assistant", content=final_text)
    db.add(assistant_msg_db)
    db.commit()

    # We'll stream the final_text as a simulated token stream (since we generated it already).
    # In a real implementation you would stream directly from the LLM.
    async def event_stream():
        words = final_text.split()
        for i in range(0, len(words), 3):   # send 3 words at a time
            chunk = " ".join(words[i:i+3]) + " "
            yield f"data: {chunk}\n\n"
            await asyncio.sleep(0.1)        # simulate delay

    return StreamingResponse(event_stream(), media_type="text/event-stream")