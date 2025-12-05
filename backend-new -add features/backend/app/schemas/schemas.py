# backend/app/schemas/schemas.py
import uuid
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Any
from app.models.models import QuestionType

class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None

class UserCreate(UserBase):
    google_id: str

class User(UserBase):
    id: uuid.UUID
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# --- Add the schemas below ---

class MessageBase(BaseModel):
    role: str
    content: str
    question_image_url: Optional[str] = None
    answer_image_url: Optional[str] = None
    youtube_link: Optional[str] = None

class Message(MessageBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    title: str

class Conversation(ConversationBase):
    id: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConversationWithMessages(Conversation):
    messages: list[Message] = []


# --- Admin CRUD Schemas ---

# --- Subject Schemas ---
class SubjectBase(BaseModel):
    name: str

class SubjectCreate(SubjectBase):
    pass

class Subject(SubjectBase):
    id: uuid.UUID
    class Config:
        from_attributes = True

# --- Theory Schemas ---
class TheoryBase(BaseModel):
    unit: str
    main_heading: str
    sub_heading: Optional[str] = None
    content: str

class TheoryCreate(TheoryBase):
    subject_id: uuid.UUID

class TheoryUpdate(TheoryBase):
    pass

class Theory(TheoryBase):
    id: uuid.UUID
    subject_id: uuid.UUID
    class Config:
        from_attributes = True

# --- Past Paper Schemas ---
class PastPaperQuestionBase(BaseModel):
    year: int
    question_type: QuestionType
    question_number: int
    question_unit: Optional[str] = None
    question_data: Any 
    answer_data: Any
    relevant_theory: Optional[str] = None
    question_image_url: Optional[str] = None
    answer_image_url: Optional[str] = None
    youtube_link: Optional[str] = None

class PastPaperQuestionCreate(PastPaperQuestionBase):
    subject_id: uuid.UUID
    
class PastPaperQuestionUpdate(BaseModel):
    year: Optional[int] = None
    question_type: Optional[QuestionType] = None
    question_number: Optional[int] = None
    question_unit: Optional[str] = None
    question_data: Optional[Any] = None
    answer_data: Optional[Any] = None
    relevant_theory: Optional[str] = None
    question_image_url: Optional[str] = None
    answer_image_url: Optional[str] = None
    youtube_link: Optional[str] = None

class PastPaperQuestion(PastPaperQuestionBase):
    id: uuid.UUID
    subject_id: uuid.UUID
    class Config:
        from_attributes = True

# --- Model Paper Schemas ---
class ModelPaperQuestionBase(BaseModel):
    paper_name: str
    question_type: QuestionType
    question_number: int
    question_unit: Optional[str] = None
    question_data: Any
    answer_data: Any
    relevant_theory: Optional[str] = None
    question_image_url: Optional[str] = None
    answer_image_url: Optional[str] = None
    youtube_link: Optional[str] = None

class ModelPaperQuestionCreate(ModelPaperQuestionBase):
    subject_id: uuid.UUID

class ModelPaperQuestionUpdate(BaseModel):
    paper_name: Optional[str] = None
    question_type: Optional[QuestionType] = None
    question_number: Optional[int] = None
    question_unit: Optional[str] = None
    question_data: Optional[Any] = None
    answer_data: Optional[Any] = None
    relevant_theory: Optional[str] = None
    question_image_url: Optional[str] = None
    answer_image_url: Optional[str] = None
    youtube_link: Optional[str] = None

class ModelPaperQuestion(ModelPaperQuestionBase):
    id: uuid.UUID
    subject_id: uuid.UUID
    class Config:
        from_attributes = True
