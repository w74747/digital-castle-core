FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# تثبيت المكتبات المطلوبة
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-dejavu-core \
    fonts-liberation \
    fonts-noto \
    fonts-noto-cjk \
    libpango-1.0-0 \
    libcairo2 \
    libfreetype6 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# تثبيت Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# تثبيت Playwright
RUN playwright install chromium

# نسخ التطبيق
COPY . .

# إنشاء مجلدات المشروع
RUN mkdir -p assets config app

EXPOSE 8000

# تشغيل FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
