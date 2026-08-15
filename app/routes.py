from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Task, Webhook, Log
from app.auth import create_access_token, hash_password, verify_password, verify_token
from app.schemas import UserCreate, UserLogin, TaskCreate, TaskUpdate, WebhookCreate
from app.prime_agent_adapter import prime_agent_system
import httpx
import json

router = APIRouter(prefix="/api", tags=["api"])

# Auth endpoints
@router.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User exists")
    
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"id": db_user.id, "username": db_user.username}

@router.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token(data={"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}

# Task endpoints
@router.get("/tasks")
async def get_tasks(db: Session = Depends(get_db), username: str = Depends(verify_token)):
    tasks = db.query(Task).all()
    return {"tasks": [{"id": t.id, "title": t.title, "agent": t.agent, "status": t.status, "created_at": t.created_at} for t in tasks]}

@router.post("/tasks")
async def create_task(task: TaskCreate, db: Session = Depends(get_db), username: str = Depends(verify_token)):
    db_task = Task(title=task.title, description=task.description, agent=task.agent, status="pending")
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return {"id": db_task.id, "status": "created"}

@router.put("/tasks/{task_id}")
async def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db), username: str = Depends(verify_token)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.status = task_update.status
    if task_update.result:
        task.result = task_update.result
    db.commit()
    return {"message": "Task updated"}

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db), username: str = Depends(verify_token)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}

# Agent execution
@router.post("/agents/{agent_name}/execute")
async def execute_agent(agent_name: str, prompt: str, db: Session = Depends(get_db), username: str = Depends(verify_token)):
    task = Task(title=f"Execute {agent_name}", agent=agent_name, status="running")
    db.add(task)
    db.commit()
    db.refresh(task)
    
    try:
        result = await prime_agent_system.route_task({"type": "execute", "agent": agent_name, "prompt": prompt})
        task.status = "completed"
        task.result = {"output": result}
    except Exception as e:
        task.status = "failed"
        task.result = {"error": str(e)}
    
    db.commit()
    return {"task_id": task.id, "status": task.status}

# Analytics
@router.get("/analytics")
async def analytics(db: Session = Depends(get_db), username: str = Depends(verify_token)):
    total = db.query(Task).count()
    completed = db.query(Task).filter(Task.status == "completed").count()
    failed = db.query(Task).filter(Task.status == "failed").count()
    pending = db.query(Task).filter(Task.status == "pending").count()
    
    return {
        "total_tasks": total,
        "completed": completed,
        "failed": failed,
        "pending": pending,
        "completion_rate": (completed / total * 100) if total > 0 else 0
    }

# Webhooks
@router.post("/webhooks")
async def create_webhook(webhook: WebhookCreate, db: Session = Depends(get_db), username: str = Depends(verify_token)):
    db_webhook = Webhook(url=webhook.url, event=webhook.event, user_id=1)
    db.add(db_webhook)
    db.commit()
    return {"id": db_webhook.id}

@router.get("/webhooks")
async def get_webhooks(db: Session = Depends(get_db), username: str = Depends(verify_token)):
    webhooks = db.query(Webhook).all()
    return {"webhooks": [{"id": w.id, "url": w.url, "event": w.event} for w in webhooks]}

# Logs
@router.get("/logs")
async def get_logs(task_id: int = None, db: Session = Depends(get_db), username: str = Depends(verify_token)):
    query = db.query(Log)
    if task_id:
        query = query.filter(Log.task_id == task_id)
    logs = query.limit(100).all()
    return {"logs": [{"level": l.level, "message": l.message, "created_at": l.created_at} for l in logs]}
