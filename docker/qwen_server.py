# docker/qwen_server.py
"""Qwen Local API Server"""
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Qwen Server")

logger.info("Loading Qwen model...")
model_name = "Qwen/Qwen2.5-3B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir="/models")
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    cache_dir="/models",
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="auto"
)
logger.info("Model loaded successfully")

class ChatRequest(BaseModel):
    model: str
    messages: list
    max_tokens: int = 4096
    temperature: float = 0.7

class ChatResponse(BaseModel):
    choices: list

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    prompt = request.messages[-1]["content"]
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=0.95,
            do_sample=True
        )
    
    response_text = tokenizer.decode(
        output[0][inputs["input_ids"].shape[1]:],
        skip_special_tokens=True
    )
    
    return ChatResponse(choices=[{"message": {"content": response_text}}])

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
