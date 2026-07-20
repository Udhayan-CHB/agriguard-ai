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
        "problem": farm.problem or request.message,
    }
    return conversation, state


@router.post("/", response_model=ChatResponse)
def chat_with_agent(request: ChatRequest, db: Session = Depends(get_db)):
    conversation, initial_state = get_chat_context(request, db)
    result = agent_graph.invoke(initial_state)
    final_response = result.get("final_response", "I couldn't create advice for that request.")
    db.add_all([
        Message(conversation_id=conversation.id, role="user", content=request.message.strip()),
        Message(conversation_id=conversation.id, role="assistant", content=final_response),
    ])
    db.commit()
    used_agents = ", ".join(result.get("required_agents", [])) or "Supervisor"
    return ChatResponse(reply=final_response, agent_path=f"Supervisor -> {used_agents} -> Reflection")


@router.post("/stream")
async def chat_stream(request: ChatRequest, db: Session = Depends(get_db)):
    response = chat_with_agent(request, db)

    async def event_stream():
        for word in response.reply.split():
            yield f"data: {word} \\n\\n"
            await asyncio.sleep(0.01)
        yield "event: done\\ndata: complete\\n\\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
