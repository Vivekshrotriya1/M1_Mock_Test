import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from Section_1_to_3.database import engine, get_db, Base
from Section_1_to_3.models import StudentDB, Student, StudentResponse

# Auto create students table
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Student Management API",
    description="FastAPI + SQLite + SQLAlchemy",
    version="2.0.0"
)

@app.get('/')
def home():
    return {"message": "Welcome to Student Management API"}

#Get All Students
@app.get('/students')
def get_students(db: Session = Depends(get_db)):
    students = db.query(StudentDB).all()
    return JSONResponse(
        status_code=200,
        content={
            "message": "Students fetched successfully",
            "count": len(students),
            "data": [StudentResponse.from_orm(s).dict() for s in students]
        }
    )

#Create Student
@app.post('/students', status_code=201)
def create_student(student: Student, db: Session = Depends(get_db)):
    new_student = StudentDB(**student.dict())
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return JSONResponse(
        status_code=201,
        content={
            "message": "Student created successfully",
            "data": StudentResponse.from_orm(new_student).dict()
        }
    )

#Search by Name
@app.get('/students/search')
def search_students(course: Optional[str] = None, db: Session = Depends(get_db)):
    if not course:
        raise HTTPException(status_code=400, detail="Please provide a course keyword")

    students = db.query(StudentDB).filter(
        StudentDB.course.ilike(f"%{course}%") 
    ).all()

    if not students:
        raise HTTPException(status_code=404, detail=f"No students found with name: {course}")

    return JSONResponse(
        status_code=200,
        content={
            "message": f"Students found with course containing: {course}",
            "count": len(students),
            "data": [StudentResponse.from_orm(s).dict() for s in students]
        }
    )

#Get Student by ID
@app.get('/students/{id}')
def get_student(id: int, db: Session = Depends(get_db)):
    student = db.query(StudentDB).filter(StudentDB.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return JSONResponse(
        status_code=200,
        content={
            "message": f"Student with id {id} fetched successfully",
            "data": StudentResponse.from_orm(student).dict()
        }
    )

#Update Student
@app.put('/students/{id}')
def update_student(id: int, updated: Student, db: Session = Depends(get_db)):
    student = db.query(StudentDB).filter(StudentDB.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    for key, value in updated.dict().items():
        setattr(student, key, value)

    db.commit()
    db.refresh(student)

    return JSONResponse(
        status_code=200,
        content={
            "message": f"Student with id {id} updated successfully",
            "data": StudentResponse.from_orm(student).dict()
        }
    )

#Delete Student
@app.delete('/students/{id}')
def delete_student(id: int, db: Session = Depends(get_db)):
    student = db.query(StudentDB).filter(StudentDB.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    db.delete(student)
    db.commit()

    return JSONResponse(
        status_code=200,
        content={
            "message": f"Student with id {id} deleted successfully",
            "data": StudentResponse.from_orm(student).dict()
        }
    )
