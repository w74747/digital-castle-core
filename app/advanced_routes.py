from fastapi import APIRouter, Depends, WebSocket, HTTPException, Header
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Task, Webhook
from app.auth import verify_token
from app.websocket import manager
from app.email_service import email_service
from app.cache import cache
import httpx
import json

router = APIRouter(prefix="/api/v2", tags=["advanced"])

# WebSocket endpoint
@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast({"message": data, "type": "broadcast"})
    except Exception:
        manager.disconnect(websocket)

# Rate limited endpoints
@router.get(
    "/tasks",
    dependencies=[Depends(RateLimiter(times=100, seconds=60))]
)
@cache(expire=60)
async def get_tasks_cached(db: Session = Depends(get_db), username: str = Depends(verify_token)):
    tasks = db.query(Task).limit(100).all()
    return {"tasks": [{"id": t.id, "title": t.title, "status": t.status} for t in tasks]}

# Advanced task creation with notifications
@router.post("/tasks/advanced")
async def create_task_advanced(
    title: str,
    description: str,
    agent: str,
    notify_email: str = None,
    webhook_url: str = None,
    db: Session = Depends(get_db),
    username: str = Depends(verify_token)
):
    task = Task(title=title, description=description, agent=agent, status="pending")
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Send email notification
    if notify_email:
        await email_service.send_task_notification(notify_email, title, "pending")
    
    # Call webhook
    if webhook_url:
        try:
            async with httpx.AsyncClient() as client:
                await client.post(webhook_url, json={"task_id": task.id, "status": "created"})
        except Exception:
            pass
    
    # Broadcast via WebSocket
    await manager.broadcast({
        "type": "task_created",
        "task_id": task.id,
        "title": title,
        "agent": agent
    })
    
    return {"id": task.id, "status": "created"}

# Batch operations
@router.post("/tasks/batch")
async def create_tasks_batch(
    tasks_data: list,
    db: Session = Depends(get_db),
    username: str = Depends(verify_token)
):
    created_tasks = []
    for task_data in tasks_data:
        task = Task(
            title=task_data["title"],
            description=task_data.get("description", ""),
            agent=task_data.get("agent", "Developer"),
            status="pending"
        )
        db.add(task)
        created_tasks.append(task)
    
    db.commit()
    return {"created": len(created_tasks), "tasks": [{"id": t.id} for t in created_tasks]}

# Advanced analytics
@router.get("/analytics/advanced")
@cache(expire=300)
async def analytics_advanced(db: Session = Depends(get_db), username: str = Depends(verify_token)):
    total = db.query(Task).count()
    completed = db.query(Task).filter(Task.status == "completed").count()
    failed = db.query(Task).filter(Task.status == "failed").count()
    running = db.query(Task).filter(Task.status == "running").count()
    
    by_agent = {}
    tasks = db.query(Task).all()
    for task in tasks:
        agent = task.agent
        if agent not in by_agent:
            by_agent[agent] = {"total": 0, "completed": 0}
        by_agent[agent]["total"] += 1
        if task.status == "completed":
            by_agent[agent]["completed"] += 1
    
    return {
        "summary": {
            "total": total,
            "completed": completed,
            "failed": failed,
            "running": running,
            "completion_rate": (completed / total * 100) if total > 0 else 0
        },
        "by_agent": by_agent,
        "efficiency": {
            "avg_completion_time": 120,
            "success_rate": (completed / total * 100) if total > 0 else 0
        }
    }

# Export tasks
@router.get("/tasks/export/csv")
async def export_tasks_csv(db: Session = Depends(get_db), username: str = Depends(verify_token)):
    import csv
    from io import StringIO
    
    tasks = db.query(Task).all()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Title", "Agent", "Status", "Created"])
    
    for task in tasks:
        writer.writerow([task.id, task.title, task.agent, task.status, task.created_at])
    
    return {"csv": output.getvalue()}

# Search tasks
@router.get("/tasks/search")
async def search_tasks(
    q: str,
    db: Session = Depends(get_db),
    username: str = Depends(verify_token)
):
    tasks = db.query(Task).filter(Task.title.contains(q)).limit(20).all()
    return {"results": [{"id": t.id, "title": t.title, "agent": t.agent} for t in tasks]}

# Audit logs
@router.get("/audit")
async def get_audit_logs(
    limit: int = 100,
    db: Session = Depends(get_db),
    username: str = Depends(verify_token)
):
    from app.models import Log
    logs = db.query(Log).order_by(Log.created_at.desc()).limit(limit).all()
    return {"logs": [{"level": l.level, "message": l.message, "created_at": l.created_at} for l in logs]}
