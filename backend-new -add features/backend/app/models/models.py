# backend/app/models/models.py
import uuid
from sqlalchemy import (Column, String, DateTime, Text, func, text, ForeignKey, 
                        Integer, Enum as PyEnum, Index)
import enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, TSVECTOR
from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    google_id = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    access_token = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    
    # Add relationship to conversations
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String, default="New Conversation")
    created_at = Column(DateTime, server_default=func.now())
    
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False) # 'user' or 'model'
    content = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    question_image_url = Column(String, nullable=True)
    answer_image_url = Column(String, nullable=True)
    youtube_link = Column(String, nullable=True)
    
    conversation = relationship("Conversation", back_populates="messages")


# --- Educational Content Models (sources schema) ---

source_schema = "sources"

class Subject(Base):
    __tablename__ = 'subjects'
    __table_args__ = {'schema': source_schema}
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String, unique=True, nullable=False) # e.g., 'Physics', 'Chemistry'

class Theory(Base):
    __tablename__ = 'theories'
    __table_args__ = {'schema': source_schema}
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    subject_id = Column(UUID(as_uuid=True), ForeignKey(f'{source_schema}.subjects.id'), nullable=False)
    unit = Column(String, nullable=False)
    main_heading = Column(String, nullable=False)
    sub_heading = Column(String)
    content = Column(Text, nullable=False)
    
    subject = relationship("Subject")

class QuestionType(enum.Enum):
    mcq = "mcq"
    structure = "structure"
    essay = "essay"

class PastPaperQuestion(Base):
    __tablename__ = 'past_papers'
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    subject_id = Column(UUID(as_uuid=True), ForeignKey(f'{source_schema}.subjects.id'), nullable=False)
    year = Column(Integer, nullable=False)
    question_type = Column(PyEnum(QuestionType, name='question_type_enum', schema=source_schema), nullable=False)
    question_number = Column(Integer, nullable=False)
    question_unit = Column(String)
    
    question_data = Column(JSONB, nullable=False)
    answer_data = Column(JSONB, nullable=False)
    relevant_theory = Column(Text)
    question_image_url = Column(String, nullable=True)
    answer_image_url = Column(String, nullable=True)
    youtube_link = Column(String, nullable=True)

    subject = relationship("Subject")
    search_vector = Column(TSVECTOR)

    __table_args__ = (
        Index('ix_sources_past_papers_search_vector', 'search_vector', postgresql_using='gin'),
        {'schema': source_schema}
    )

class ModelPaperQuestion(Base):
    __tablename__ = 'model_papers'
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    subject_id = Column(UUID(as_uuid=True), ForeignKey(f'{source_schema}.subjects.id'), nullable=False)
    paper_name = Column(String, nullable=False)
    question_type = Column(PyEnum(QuestionType, name='question_type_enum', schema=source_schema), nullable=False)
    question_number = Column(Integer, nullable=False)
    question_unit = Column(String)
    
    question_data = Column(JSONB, nullable=False)
    answer_data = Column(JSONB, nullable=False)
    relevant_theory = Column(Text)
    question_image_url = Column(String, nullable=True)
    answer_image_url = Column(String, nullable=True)
    youtube_link = Column(String, nullable=True)

    subject = relationship("Subject")
    search_vector = Column(TSVECTOR)
    
    __table_args__ = (
        Index('ix_sources_model_papers_search_vector', 'search_vector', postgresql_using='gin'),
        {'schema': source_schema}
    )
