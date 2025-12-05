# backend/main.py
import os
from fastapi import FastAPI, Depends, HTTPException, Request, status, WebSocket, WebSocketDisconnect, Response, Form
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
import json

from .import schemas
from . import crud, models, auth, prompts
from .database import engine, SessionLocal
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

import asyncio
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from .routers import subjects, theories, past_papers, model_papers
from .tools import (GetPastPaperQuestionTool, GetModelPaperQuestionTool,
                   GetTheoryTool, SearchQuestionsByTopicTool)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}


model = genai.GenerativeModel('gemini-2.5-flash', safety_settings=safety_settings, system_instruction=prompts.UNIFIED_SYSTEM_PROMPT)
available_tools = [
    GetPastPaperQuestionTool,
    GetModelPaperQuestionTool,
    GetTheoryTool,
    SearchQuestionsByTopicTool
]




app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))
app.add_middleware(CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)

@app.get("/auth/google")
async def login_google(request: Request):
    redirect_uri = request.url_for('auth_google_callback')
    return await auth.oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/callback", name="auth_google_callback")
async def auth_google_callback(request: Request, db: Session = Depends(auth.get_db)):
    try:
        token = await auth.oauth.google.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Could not validate credentials from Google")

    user_info = token.get('userinfo')
    if not user_info:
        raise HTTPException(status_code=400, detail="User info not in token")

    google_id = user_info['sub']
    email = user_info['email']
    full_name = user_info['name']

    db_user = crud.get_user_by_google_id(db, google_id=google_id)
    if not db_user:
        user_create = schemas.UserCreate(google_id=google_id, email=email, full_name=full_name)
        db_user = crud.create_user(db, user_create)

    access_token = auth.create_access_token(data={"sub": db_user.google_id})
    refresh_token = auth.create_refresh_token(data={"sub": db_user.google_id})

    # Store tokens in the database
    db_user.access_token = access_token
    db_user.refresh_token = refresh_token
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    response = RedirectResponse(
        url=f"http://localhost:3000/auth/callback?access_token={access_token}&refresh_token={refresh_token}"
    )
    return response

@app.post("/token/refresh", response_model=schemas.Token)
async def refresh_token(refresh_token: str = Form(...), db: Session = Depends(auth.get_db)):
    user = auth.verify_refresh_token(refresh_token, db)
    access_token = auth.create_access_token(data={"sub": user.google_id})

    # Update access_token in the database
    user.access_token = access_token
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"access_token": access_token, "token_type": "bearer"}

# A test route to check if authentication works
@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user


# === START: NEW CONVERSATION & MESSAGE ROUTES ===

@app.post("/conversations/", response_model=schemas.Conversation, status_code=status.HTTP_201_CREATED)
def create_new_conversation(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(auth.get_db)):
    conversation = crud.create_conversation(db=db, user_id=current_user.id)
    return conversation

@app.get("/conversations/", response_model=list[schemas.Conversation])
def get_user_conversations(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(auth.get_db)):
    return crud.get_conversations_by_user(db=db, user_id=current_user.id)

@app.get("/conversations/{conversation_id}", response_model=schemas.ConversationWithMessages)
def get_a_conversation(conversation_id: str, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(auth.get_db)):
    conversation = crud.get_conversation(db=db, conversation_id=conversation_id, user_id=current_user.id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = crud.get_messages_by_conversation(db=db, conversation_id=conversation_id)
    conversation.messages = messages
    return conversation

@app.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_a_conversation(conversation_id: str, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(auth.get_db)):
    success = crud.delete_conversation(db=db, conversation_id=conversation_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# === END: NEW CONVERSATION & MESSAGE ROUTES ===


# --- Admin API Routers ---
app.include_router(subjects.router)
app.include_router(theories.router)
app.include_router(past_papers.router)
app.include_router(model_papers.router)

@app.websocket("/ws/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str, db: Session = Depends(auth.get_db)):
    await websocket.accept()

    token = websocket.query_params.get('token')
    if not token:
        await websocket.close(code=1008, reason="Token not provided")
        return

    try:
        user = auth.get_current_user(token=token, db=db)
    except HTTPException:
        await websocket.close(code=1008, reason="Authentication failed")
        return

    conversation = crud.get_conversation(db, conversation_id=conversation_id, user_id=user.id)
    if not conversation:
        await websocket.close(code=1008, reason="Conversation not found")
        return

    messages = crud.get_messages_by_conversation(db, conversation_id=conversation.id)
    history = [{"role": msg.role, "parts": [msg.content]} for msg in messages]
    chat = model.start_chat(history=history)

    try:
        while True:
            user_prompt = await websocket.receive_text()
            # --- START: DYNAMIC TITLE GENERATION ---
            # Check if this is the first message in a new conversation
            is_new_conversation = conversation.title == "New Conversation" and len(history) == 0

            crud.create_message(db, conversation_id=conversation.id, role="user", content=user_prompt)

            if is_new_conversation:
                # Generate a title
                title_prompt = f"Based on the following user query, create a short, descriptive title (5 words or less) for the conversation. Do not use quotes or any special formatting. Just return the text of the title. User Query: \"{user_prompt}\""
                title_response = model.generate_content(title_prompt)
                new_title = title_response.text.strip().replace('"', '')
                crud.update_conversation_title(db, conversation_id=conversation.id, title=new_title)
            # --- END: DYNAMIC TITLE GENERATION ---

            history_messages = crud.get_messages_by_conversation(db, conversation_id=conversation.id, limit=4)
            chat_history_for_prompt = "\n".join([f"{msg.role}: {msg.content}" for msg in history_messages])

            response = model.generate_content(user_prompt, tools=available_tools)
            function_call = response.candidates[0].content.parts[0].function_call

            retrieved_context_str = "No database context was retrieved for this query."
            template = prompts.GENERAL_CHAT_TEMPLATE
            
            if function_call:
                tool_name = function_call.name
                tool_args = {key: value for key, value in function_call.args.items()}
                
                # *** NEW: LOGIC TO HANDLE MISSING INFORMATION ***
                required_params = set() 
                if tool_name == 'GetPastPaperQuesti onTool':
                    required_params = {'year', 'subject', 'question_type', 'question_number'}
                elif tool_name == 'GetModelPaperQuestionTool':
                    required_params = {'paper_name', 'subject', 'question_type', 'question_number'}

                missing_params = required_params - set(tool_args.keys())
                
                if missing_params:
                    # Ask for clarification
                    clarification_request = f"It looks like you're asking for a question, but you're missing some details. Please provide the following: {', '.join(missing_params)}."
                    await websocket.send_text(clarification_request)
                    await websocket.send_text("[END_OF_STREAM]")
                    crud.create_message(db, conversation_id=conversation.id, role="model", content=clarification_request)
                    continue


                retrieved_data = None
                if tool_name == 'GetPastPaperQuestionTool':
                    retrieved_data = crud.get_past_paper_question(db, **tool_args)
                    if retrieved_data:
                        if retrieved_data.question_type.value in ['essay', 'structure']:
                            template = prompts.ESSAY_QUESTION_TEMPLATE
                        else: # Default to MCQ/Past Paper format
                            template = prompts.PAST_PAPER_TEMPLATE

                elif tool_name == 'GetModelPaperQuestionTool':
                    retrieved_data = crud.get_model_paper_question(db, **tool_args)
                    if retrieved_data:
                        if retrieved_data.question_type.value in ['essay', 'structure']:
                            template = prompts.ESSAY_QUESTION_TEMPLATE
                        else:
                            template = prompts.PAST_PAPER_TEMPLATE

                elif tool_name == 'GetTheoryTool':
                    retrieved_data = crud.get_theory_by_topic(db, **tool_args)
                    template = prompts.THEORY_EXPLANATION_TEMPLATE
                elif tool_name == 'SearchQuestionsByTopicTool':
                    retrieved_data = crud.search_questions_by_topic(db, **tool_args)
                    template = prompts.SEARCH_RESULTS_TEMPLATE
                
                if retrieved_data:
                    context_list = retrieved_data if isinstance(retrieved_data, list) else [retrieved_data]
                    retrieved_context_str = json.dumps([
                        {k: v for k, v in r.__dict__.items() if not k.startswith('_')}
                        for r in context_list
                    ], default=str, ensure_ascii=False)

            final_prompt = template.format(
                retrieved_context=retrieved_context_str,
                chat_history=chat_history_for_prompt,
                user_prompt=user_prompt
            )
            
            response_stream = model.generate_content(final_prompt, stream=True)
            full_response = ""
            for chunk in response_stream:
                if chunk.text:
                    await websocket.send_text(chunk.text)
                    full_response += chunk.text
            
            await websocket.send_text("[END_OF_STREAM]")

            # After streaming, send the media metadata if it exists
            if retrieved_data:
                metadata = {
                    "question_image_url": retrieved_data.question_image_url,
                    "answer_image_url": retrieved_data.answer_image_url,
                    "youtube_link": retrieved_data.youtube_link,
                }
                # Send a special JSON message with the metadata
                await websocket.send_text(json.dumps({"type": "metadata", "data": metadata}))

            if full_response:
                crud.create_message(db, conversation_id=conversation.id, role="model", content=full_response,question_image_url=retrieved_data.question_image_url if retrieved_data else None,
                    answer_image_url=retrieved_data.answer_image_url if retrieved_data else None,
                    youtube_link=retrieved_data.youtube_link if retrieved_data else None)


    except WebSocketDisconnect:
        print(f"Client {user.email} disconnected from conversation {conversation_id}")