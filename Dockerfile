FROM python:3.10-slim

WORKDIR /app

# تثبيت متطلبات النظام الأساسية
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# تثبيت حزم بايثون
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ كامل ملفات المشروع
COPY . .

# أمر التشغيل
CMD ["python", "bot_orchestrator.py"]
