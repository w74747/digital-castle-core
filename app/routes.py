from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Task
from app.auth import create_access_token, verify_token
from app.prime_agent_adapter import prime_agent_system

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
    return {"tasks": [{"id": t.id, "title": t.title, "agent": t.agent, "status": t.status} for t in tasks]}

@router.post("/tasks")
async def create_task(title: str, description: str, agent: str, db: Session = Depends(get_db)):
    task = Task(title=title, description=description, agent=agent, status="pending")
    db.add(task)
    db.commit()
    return {"task_id": task.id, "status": "created"}

@router.put("/tasks/{task_id}")
async def update_task(task_id: int, status: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.status = status
        db.commit()
        return {"message": "Task updated"}
    raise HTTPException(status_code=404, detail="Task not found")

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()
        return {"message": "Task deleted"}
    raise HTTPException(status_code=404, detail="Task not found")

@router.get("/agents")
async def list_agents():
    agents = list(prime_agent_system.pool.agents.keys())
    return {"agents": agents, "count": len(agents)}

@router.post("/agents/{agent_name}/execute")
async def execute_agent(agent_name: str, task_description: str, db: Session = Depends(get_db)):
    task = Task(title=task_description, agent=agent_name, status="running")
    db.add(task)
    db.commit()
    
    result = await prime_agent_system.route_task({
        "type": "execution",
        "agent": agent_name,
        "description": task_description
    })
    
    task.status = "completed"
    db.commit()
    
    return {"result": result, "task_id": task.id}

@router.get("/analytics")
async def analytics(db: Session = Depends(get_db)):
    total_tasks = db.query(Task).count()
    completed = db.query(Task).filter(Task.status == "completed").count()
    pending = db.query(Task).filter(Task.status == "pending").count()
    
    return {
        "total_tasks": total_tasks,
        "completed": completed,
        "pending": pending,
        "completion_rate": (completed / total_tasks * 100) if total_tasks > 0 else 0
    }
