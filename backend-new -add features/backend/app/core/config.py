# backend/app/core/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    WEAVIATE_URL: str = os.getenv("WEAVIATE_URL")
    WEAVIATE_API_KEY: str = os.getenv("WEAVIATE_API_KEY")
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID")

settings = Settings()
