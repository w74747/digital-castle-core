from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Task

router = APIRouter(prefix="/api", tags=["api"])

@router.get("/tasks")
async def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return {"tasks": [{"id": t.id, "title": t.title, "agent": t.agent, "status": t.status} for t in tasks]}

@router.post("/tasks")
async def create_task(title: str, description: str, agent: str, db: Session = Depends(get_db)):
    task = Task(title=title, description=description, agent=agent, status="pending")
    db.add(task)
    db.commit()
    return {"task_id": task.id, "status": "created"}

@router.get("/analytics")
async def analytics(db: Session = Depends(get_db)):
    total = db.query(Task).count()
    completed = db.query(Task).filter(Task.status == "completed").count()
    return {"total": total, "completed": completed}
