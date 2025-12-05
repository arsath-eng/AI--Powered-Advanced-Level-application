# backend/app/main.py
from fastapi import FastAPI, Depends, HTTPException, Request, Response, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session

from app.schemas import schemas
from app.crud import crud
from app.models import models
from app.routers import subjects, theories, past_papers, model_papers, auth, conversations
from app.services.websocket_manager import websocket_endpoint
from app.core.config import settings
from app.core.security import get_current_user, get_db

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, tags=["Authentication"])
app.include_router(conversations.router, tags=["Conversations"])
app.include_router(subjects.router)
app.include_router(theories.router)
app.include_router(past_papers.router)
app.include_router(model_papers.router)

@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.websocket("/ws/{conversation_id}")
async def websocket_endpoint_route(websocket: WebSocket, conversation_id: str, db: Session = Depends(get_db)):
    await websocket_endpoint(websocket, conversation_id, db)