from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# -------- APP --------
app = FastAPI()

# -------- DATABASE SETUP --------
DATABASE_URL = "sqlite:///./students.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

# -------- DB MODEL --------
class StudentDB(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    course = Column(String, nullable=False)

# -------- CREATE TABLE --------
Base.metadata.create_all(bind=engine)

# -------- Pydantic MODEL --------
class Student(BaseModel):
    name: str = Field(..., min_length=2)
    age: int = Field(..., gt=0)
    course: str = Field(..., min_length=2)

# -------- CREATE --------
@app.post("/students", status_code=201)
def add_student(student: Student):
    db = SessionLocal()

    new_student = StudentDB(
        name=student.name,
        age=student.age,
        course=student.course
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    db.close()

    return {"message": "Student added", "id": new_student.id}

# -------- GET ALL + SEARCH --------
@app.get("/students")
def get_students(
    course: Optional[str] = Query(None),
    name: Optional[str] = Query(None)
):
    db = SessionLocal()
    query = db.query(StudentDB)

    if course:
        query = query.filter(StudentDB.course.ilike(f"%{course}%"))

    if name:
        query = query.filter(StudentDB.name.ilike(f"%{name}%"))

    students = query.all()
    db.close()

    return students

# -------- GET ONE --------
@app.get("/students/{student_id}")
def get_student(student_id: int):
    db = SessionLocal()

    student = db.query(StudentDB).filter(StudentDB.id == student_id).first()
    db.close()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return student

# -------- UPDATE --------
@app.put("/students/{student_id}")
def update_student(student_id: int, updated: Student):
    db = SessionLocal()

    student = db.query(StudentDB).filter(StudentDB.id == student_id).first()

    if not student:
        db.close()
        raise HTTPException(status_code=404, detail="Student not found")

    student.name = updated.name
    student.age = updated.age
    student.course = updated.course

    db.commit()
    db.close()

    return {"message": "Student updated"}

# -------- DELETE --------
@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    db = SessionLocal()

    student = db.query(StudentDB).filter(StudentDB.id == student_id).first()

    if not student:
        db.close()
        raise HTTPException(status_code=404, detail="Student not found")

    db.delete(student)
    db.commit()
    db.close()

    return {"message": "Student deleted"}
