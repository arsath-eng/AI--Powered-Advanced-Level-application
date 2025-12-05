# backend/app/routers/conversations.py
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
import uuid

from app import crud
from app import models
from app import schemas
from app.core.security import get_current_user, get_db

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/", response_model=schemas.Conversation, status_code=status.HTTP_201_CREATED)
def create_new_conversation(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversation = crud.create_conversation(db=db, user_id=current_user.id)
    return conversation

@router.get("/", response_model=list[schemas.Conversation])
def get_user_conversations(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.get_conversations_by_user(db=db, user_id=current_user.id)

@router.get("/{conversation_id}", response_model=schemas.ConversationWithMessages)
def get_a_conversation(conversation_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversation = crud.get_conversation(db=db, conversation_id=conversation_id, user_id=current_user.id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = crud.get_messages_by_conversation(db=db, conversation_id=conversation_id)
    conversation.messages = messages
    return conversation

@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_a_conversation(conversation_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    success = crud.delete_conversation(db=db, conversation_id=conversation_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
