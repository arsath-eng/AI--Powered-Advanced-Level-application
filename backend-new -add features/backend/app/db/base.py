# backend/app/db/base.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase

Base = declarative_base()

# Create a class that inherits from DeclarativeBase
class Base(DeclarativeBase):
    pass
