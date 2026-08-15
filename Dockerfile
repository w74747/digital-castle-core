# docker/Dockerfile.qwen
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    torch torchvision torchaudio \
    transformers \
    peft \
    bitsandbytes \
    uvicorn \
    fastapi \
    httpx

RUN mkdir -p /models

COPY docker/qwen_server.py .

RUN python -c "
from transformers import AutoTokenizer, AutoModelForCausalLM
import os

model_name = 'Qwen/Qwen2.5-3B-Instruct'
cache_dir = '/models'

print('Downloading Qwen model...')
tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
model = AutoModelForCausalLM.from_pretrained(model_name, cache_dir=cache_dir)
print('Model downloaded successfully')
"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "qwen_server.py"]
