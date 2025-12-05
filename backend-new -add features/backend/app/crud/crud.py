# backend/app/crud/crud.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import models
from app.schemas import schemas
import uuid
from typing import Optional, Type, TypeVar
from app.services.vector_store import find_similar_theories

# Define a TypeVar for our SQLAlchemy models
# This tells the type checker that any type passed must be a subclass of models.Base
ModelType = TypeVar("ModelType", bound=models.Base)


# --- Generic CRUD Helpers ---
def get_item(db: Session, model: Type[ModelType], item_id: uuid.UUID) -> Optional[ModelType]:
    return db.query(model).filter(model.id == item_id).first()

def get_items(db: Session, model: Type[ModelType], skip: int = 0, limit: int = 100) -> list[ModelType]:
    return db.query(model).offset(skip).limit(limit).all()

def create_item(db: Session, model: Type[ModelType], schema) -> ModelType:
    db_item = model(**schema.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_item(db: Session, model: Type[ModelType], item_id: uuid.UUID) -> Optional[ModelType]:
    db_item = db.query(model).filter(model.id == item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
        return db_item
    return None

def update_item(db: Session, model: Type[ModelType], item_id: uuid.UUID, schema) -> Optional[ModelType]:
    db_item = db.query(model).filter(model.id == item_id).first()
    if db_item:
        update_data = schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_item, key, value)
        db.commit()
        db.refresh(db_item)
    return db_item

# --- User Functions ---
def get_user_by_google_id(db: Session, google_id: str):
    return db.query(models.User).filter(models.User.google_id == google_id).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        google_id=user.google_id,
        email=user.email,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Conversation & Message Functions ---
def get_conversations_by_user(db: Session, user_id: uuid.UUID):
    return db.query(models.Conversation).filter(models.Conversation.user_id == user_id).order_by(models.Conversation.created_at.desc()).all()

def create_conversation(db: Session, user_id: uuid.UUID, title: str = "New Conversation"):
    new_conversation = models.Conversation(user_id=user_id, title=title)
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    return new_conversation

def get_conversation(db: Session, conversation_id: uuid.UUID, user_id: uuid.UUID):
    return db.query(models.Conversation).filter(models.Conversation.id == conversation_id, models.Conversation.user_id == user_id).first()

def delete_conversation(db: Session, conversation_id: uuid.UUID, user_id: uuid.UUID):
    conversation = db.query(models.Conversation).filter(models.Conversation.id == conversation_id, models.Conversation.user_id == user_id).first()
    if conversation:
        db.delete(conversation)
        db.commit()
        return True
    return False

def get_messages_by_conversation(db: Session, conversation_id: uuid.UUID, limit: int = None):
    query = db.query(models.Message).filter(models.Message.conversation_id == conversation_id).order_by(models.Message.created_at.desc())
    if limit:
        query = query.limit(limit)
    
    # We fetch in descending order to get the latest, then reverse for correct chronological order
    messages = query.all()
    return messages[::-1] 

def create_message(db: Session, conversation_id: uuid.UUID, role: str, content: str,question_image_url: Optional[str] = None,
    answer_image_url: Optional[str] = None,
    youtube_link: Optional[str] = None):
    db_message = models.Message(conversation_id=conversation_id, role=role, content=content,question_image_url=question_image_url,
        answer_image_url=answer_image_url,
        youtube_link=youtube_link)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


# --- RAG Tool Functions ---
def get_subject_by_name(db: Session, subject_name: str):
    return db.query(models.Subject).filter(func.lower(models.Subject.name) == func.lower(subject_name)).first()

def get_past_paper_question(db: Session, subject: str, year: int, question_type: str, question_number: int):
    subject_obj = get_subject_by_name(db, subject)
    if not subject_obj:
        return None
        
    return db.query(models.PastPaperQuestion).filter(
        models.PastPaperQuestion.subject_id == subject_obj.id,
        models.PastPaperQuestion.year == year,
        models.PastPaperQuestion.question_type == question_type.lower(),
        models.PastPaperQuestion.question_number == question_number
    ).first()

def get_model_paper_question(db: Session, subject: str, paper_name: str, question_type: str, question_number: int):
    subject_obj = get_subject_by_name(db, subject)
    if not subject_obj:
        return None
        
    return db.query(models.ModelPaperQuestion).filter(
        models.ModelPaperQuestion.subject_id == subject_obj.id,
        models.ModelPaperQuestion.paper_name == paper_name,
        models.ModelPaperQuestion.question_type == question_type.lower(),
        models.ModelPaperQuestion.question_number == question_number
    ).first()

def get_theory_by_topic(subject: str, topic: str, language: str = "tamil"):
    """
    This function is now a simple wrapper for the Weaviate vector search service.
    It no longer uses the PostgreSQL database session.
    """
    # Directly call the service that queries Weaviate
    return find_similar_theories(
        topic=topic,
        language=language,
        subject=subject
    )

def search_questions_by_topic(db: Session, subject: str, topic: str, question_type: Optional[str], year_start: Optional[int], year_end: Optional[int], limit: int = 5):
    subject_obj = get_subject_by_name(db, subject)
    if not subject_obj:
        return []

    query = db.query(models.PastPaperQuestion).filter(
        models.PastPaperQuestion.subject_id == subject_obj.id,
        models.PastPaperQuestion.search_vector.match(topic, postgresql_regconfig='simple')
    )

    if question_type:
        query = query.filter(models.PastPaperQuestion.question_type == question_type.lower())
    if year_start:
        query = query.filter(models.PastPaperQuestion.year >= year_start)
    if year_end:
        query = query.filter(models.PastPaperQuestion.year <= year_end)

    return query.order_by(models.PastPaperQuestion.year.desc()).limit(limit).all()

def update_conversation_title(db: Session, conversation_id: uuid.UUID, title: str):
    conversation = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    if conversation:
        conversation.title = title
        db.commit()
        db.refresh(conversation)
        return conversation
    return None
