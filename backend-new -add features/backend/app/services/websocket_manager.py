# backend/app/services/websocket_manager.py
from fastapi import WebSocket, Depends, HTTPException, WebSocketDisconnect
from sqlalchemy.orm import Session
import json
import asyncio
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from app.crud import crud
from app.models import models
from app import prompts
from app.core.config import settings
from app.core.security import get_current_user, get_db
from tools.tools import (GetPastPaperQuestionTool, GetModelPaperQuestionTool,
                   GetTheoryTool, SearchQuestionsByTopicTool)

# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)
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

async def websocket_endpoint(websocket: WebSocket, conversation_id: str, db: Session = Depends(get_db)):
    await websocket.accept()

    token = websocket.query_params.get('token')
    if not token:
        await websocket.close(code=1008, reason="Token not provided")
        return

    try:
        user = get_current_user(token=token, db=db)
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
                try:
                    title_prompt = f"Based on the following user query, create a short, descriptive title (5 words or less) for the conversation. Do not use quotes or any special formatting. Just return the text of the title. User Query: \"{user_prompt}\""
                    title_response = model.generate_content(title_prompt)
                    new_title = title_response.text.strip().replace('"', '')
                    crud.update_conversation_title(db, conversation_id=conversation.id, title=new_title)
                except Exception as e:
                    print(f"Title generation error: {str(e)}")
                    # Continue without title generation if it fails
            # --- END: DYNAMIC TITLE GENERATION ---

            history_messages = crud.get_messages_by_conversation(db, conversation_id=conversation.id, limit=4)
            chat_history_for_prompt = "\n".join([f"{msg.role}: {msg.content}" for msg in history_messages])

            try:
                response = model.generate_content(user_prompt, tools=available_tools)
                function_call = response.candidates[0].content.parts[0].function_call if response.candidates and response.candidates[0].content.parts else None
            except Exception as e:
                print(f"Function call generation error: {str(e)}")
                function_call = None

            retrieved_context_str = "No database context was retrieved for this query."
            template = prompts.GENERAL_CHAT_TEMPLATE
            
            if function_call:
                tool_name = function_call.name
                tool_args = {key: value for key, value in function_call.args.items()}
                
                # *** NEW: LOGIC TO HANDLE MISSING INFORMATION ***
                required_params = set() 
                if tool_name == 'GetPastPaperQuestionTool':
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
                    retrieved_data = crud.get_theory_by_topic(**tool_args)
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
            
            try:
                response_stream = model.generate_content(final_prompt, stream=True)
                full_response = ""
                for chunk in response_stream:
                    if chunk.text:
                        await websocket.send_text(chunk.text)
                        full_response += chunk.text
            except Exception as e:
                print(f"AI generation error: {str(e)}")
                error_message = "Sorry, I encountered an error while generating a response. Please try again."
                await websocket.send_text(error_message)
                full_response = error_message
            
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
    except Exception as e:
        print(f"WebSocket error for user {user.email} in conversation {conversation_id}: {str(e)}")
        try:
            await websocket.close(code=1011, reason=f"Server error: {str(e)}")
        except:
            pass
    finally:
        print(f"WebSocket connection ended for user {user.email} in conversation {conversation_id}")
