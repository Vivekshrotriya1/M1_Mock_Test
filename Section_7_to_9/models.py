from sqlalchemy import Column, Integer, String
from database import Base
from pydantic import BaseModel
from typing import Optional

# SQLAlchemy Model
class StudentDB(Base):
    __tablename__ = "students"

    id     = Column(Integer, primary_key=True, index=True)
    name   = Column(String, nullable=False)
    age    = Column(Integer, nullable=False)
    course = Column(String, nullable=True)

# Pydantic request model
class Student(BaseModel):
    name: str
    age: int
    course: Optional[str] = None

# Pydantic response model
class StudentResponse(BaseModel):
    id: int
    name: str
    age: int
    course: Optional[str] = None

    class Config:
        from_attributes = True 