from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Task
from app.auth import create_access_token, verify_token

router = APIRouter(prefix="/api", tags=["api"])

@router.post("/register")
async def register(username: str, email: str, password: str, db: Session = Depends(get_db)):
    user = User(username=username, email=email, password=password)
    db.add(user)
    db.commit()
    return {"message": "User created", "user_id": user.id}

@router.post("/login")
async def login(username: str, password: str):
    token = create_access_token({"username": username})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/tasks")
async def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return {"tasks": tasks}

@router.post("/tasks")
async def create_task(title: str, agent: str, db: Session = Depends(get_db)):
    task = Task(title=title, agent=agent, status="pending")
    db.add(task)
    db.commit()
    return {"task_id": task.id}
