# backend/app/api/endpoints/chat.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional
from agents.agent import ChatbotAgent, QueryParameters
from sqlalchemy.orm import Session

from ..models.base import get_db
from ..models.user import User
from ..schemas.user import UserResponse

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
agent = ChatbotAgent()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    success: bool
    error: Optional[str] = None

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    # In a real app, you would verify the token and get the user
    # For simplicity, we'll assume the user is authenticated
    user = db.query(User).filter(User.username == "testuser").first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    params = QueryParameters(query=request.message, user_id=user.id)
    result = agent.process_query(params)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return ChatResponse(
        response=result["response"],
        success=True
    )