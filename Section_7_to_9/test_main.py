import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Section_1_to_3')))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_setup():
    """Create tables before test, drop after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_setup):
    """Create test client with overridden DB"""
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def sample_student():
    """Sample student data"""
    return {
        "name": "Ayan",
        "age": 21,
        "course": "AI"
    }


def is_valid_student(student: dict) -> bool:
    """Validates student has required fields"""
    return all(key in student for key in ["name", "age", "course"])

def test_is_valid_student():
    assert is_valid_student({"name": "Ayan", "age": 21, "course": "AI"}) == True
    assert is_valid_student({"name": "Ayan"}) == False
    assert is_valid_student({}) == False

# ─── API Endpoint Tests ──────────────────────────────

def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Student Management API"}

def test_create_student(client, sample_student):
    response = client.post("/students", json=sample_student)
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["name"] == "Ayan"
    assert data["age"] == 21
    assert data["course"] == "AI"
    assert "id" in data

def test_get_all_students(client, sample_student):
    client.post("/students", json=sample_student)
    response = client.get("/students")
    assert response.status_code == 200
    assert response.json()["count"] >= 1

def test_get_student_by_id(client, sample_student):
    post_res = client.post("/students", json=sample_student)
    student_id = post_res.json()["data"]["id"]

    response = client.get(f"/students/{student_id}")
    assert response.status_code == 200
    assert response.json()["data"]["id"] == student_id

def test_get_student_not_found(client):
    response = client.get("/students/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found"

def test_update_student(client, sample_student):
    post_res = client.post("/students", json=sample_student)
    student_id = post_res.json()["data"]["id"]

    updated = {"name": "Ayan Khan", "age": 22, "course": "ML"}
    response = client.put(f"/students/{student_id}", json=updated)
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Ayan Khan"
    assert response.json()["data"]["course"] == "ML"

def test_delete_student(client, sample_student):
    post_res = client.post("/students", json=sample_student)
    student_id = post_res.json()["data"]["id"]

    response = client.delete(f"/students/{student_id}")
    assert response.status_code == 200

    # Verify deleted
    get_res = client.get(f"/students/{student_id}")
    assert get_res.status_code == 404

def test_search_student(client, sample_student):
    client.post("/students", json=sample_student)
    response = client.get("/students/search?course=AI")  
    assert response.status_code == 200
    assert response.json()["count"] >= 1

def test_search_student_not_found(client):
    response = client.get("/students/search?course=xyz123")  
    assert response.status_code == 404