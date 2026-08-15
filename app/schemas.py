from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class TaskCreate(BaseModel):
    title: str
    description: str = ""
    agent: str

class TaskUpdate(BaseModel):
    status: str
    result: dict = None

class WebhookCreate(BaseModel):
    url: str
    event: str

class Token(BaseModel):
    access_token: str
    token_type: str
