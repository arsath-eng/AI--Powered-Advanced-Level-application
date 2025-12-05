# backend/tools/tools.py
from pydantic import BaseModel, Field
from typing import Optional

class GetPastPaperQuestionTool(BaseModel):
    """Tool to fetch a specific past paper question from the database."""
    subject: str = Field(..., description="The subject of the question, e.g., 'Physics', 'Chemistry'.")
    year: int = Field(..., description="The year of the past paper.")
    question_type: str = Field(..., description="The type of question: 'mcq', 'structure', or 'essay'.")
    question_number: int = Field(..., description="The specific question number.")

class GetModelPaperQuestionTool(BaseModel):
    """Tool to fetch a specific model paper question."""
    subject: str = Field(..., description="The subject of the question.")
    paper_name: str = Field(..., description="The name of the model paper, e.g., '2025 Model Paper A'.")
    question_type: str = Field(..., description="The type of question: 'mcq', 'structure', or 'essay'.")
    question_number: int = Field(..., description="The specific question number.")

class GetTheoryTool(BaseModel):
    """Tool to fetch a theory explanation on a specific topic."""
    subject: str = Field(..., description="The subject of the theory, e.g., 'Physics', 'Chemistry'.")
    topic: str = Field(..., description="The unit, main heading, or sub-heading of the theory to search for.")
    language: str = Field("tamil", description="The language of the theory: 'tamil', 'sinhala', or 'english'.")

class SearchQuestionsByTopicTool(BaseModel):
    """Tool to search for past paper or model paper questions related to a topic."""
    subject: str = Field(..., description="The subject to search within.")
    topic: str = Field(..., description="The keyword or topic to search for, e.g., 'friction', 'calorimetry'.")
    question_type: Optional[str] = Field(None, description="Filter by question type: 'mcq', 'structure', or 'essay'.")
    year_start: Optional[int] = Field(None, description="The starting year for the search range.")
    year_end: Optional[int] = Field(None, description="The ending year for the search range.")
