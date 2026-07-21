from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import Conversation, Message, User, FarmProfile
from app.schemas.chat import ChatRequest, ChatResponse
from app.agents.graph import agent_graph
from app.core.config import settings
from langchain_core.messages import HumanMessage, AIMessage
from fastapi.responses import StreamingResponse
import asyncio
from app.api.deps import get_current_user, get_db

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_chat_context(request: ChatRequest, db: Session):
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Save a farm profile first.")
    farm = db.query(FarmProfile).filter(FarmProfile.id == request.farm_profile_id, FarmProfile.user_id == user.id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm profile not found")
    conversation = db.query(Conversation).filter(Conversation.user_id == user.id, Conversation.farm_profile_id == farm.id).first()
    if not conversation:
        conversation = Conversation(user_id=user.id, farm_profile_id=farm.id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    history = [HumanMessage(content=m.content) if m.role == "user" else AIMessage(content=m.content) for m in conversation.messages[-settings.MAX_CHAT_HISTORY:]]
    state = {
        "messages": history + [HumanMessage(content=request.message.strip())],
        "farm_id": farm.id, "username": request.username, "location": farm.location,
        "crop": farm.crop, "farm_size_hectares": farm.farm_size_hectares,
        # Each chat turn must be analysed on its own. The saved profile concern
        # belongs in reports, not as a replacement for every new question.
        "problem": request.message.strip(),
    }
    return conversation, state


@router.post("/", response_model=ChatResponse)
def chat_with_agent(request: ChatRequest, db: Session = Depends(get_db)):
    # Validate user
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # If no farm profile, use generic defaults
    location = "unknown"
    crop = "unknown"
    problem = request.message
    farm_size = 1.0
    farm = None

    if request.farm_profile_id:
        farm = db.query(FarmProfile).filter(
            FarmProfile.id == request.farm_profile_id,
            FarmProfile.user_id == user.id
        ).first()
        if not farm:
            raise HTTPException(status_code=404, detail="Farm profile not found")
        location = farm.location
        crop = farm.crop
        problem = farm.problem or request.message
        farm_size = farm.farm_size_hectares
    # else: stay with generic defaults

    # Retrieve/create conversation (link to farm if present, else user-wide)
    conversation = db.query(Conversation).filter(
        Conversation.user_id == user.id,
        Conversation.farm_profile_id == (request.farm_profile_id if farm else None)
    ).first()
    if not conversation:
        conversation = Conversation(
            user_id=user.id,
            farm_profile_id=request.farm_profile_id if farm else None
        )
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

    all_messages = previous_messages + [HumanMessage(content=request.message)]

    initial_state = {
        "messages": all_messages,
        "farm_id": request.farm_profile_id,
        "username": request.username,
        "location": location,
        "crop": crop,
        "farm_size_hectares": farm_size,
        "problem": problem,
    }

    result = agent_graph.invoke(initial_state)
    final_response = result.get("final_response", "I'm not sure how to help with that.")

    # Save messages
    msg_user = Message(conversation_id=conversation.id, role="user", content=request.message)
    db.add(msg_user)
    msg_ai = Message(conversation_id=conversation.id, role="assistant", content=final_response)
    db.add(msg_ai)
    db.commit()

    return ChatResponse(reply=final_response, agent_path="Supervisor → Executor → Reflection")