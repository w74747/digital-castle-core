# Build Stage: استخراج الحد الأدنى من المكتبات المطلوبة
FROM python:3.11-slim as builder

# تثبيت المكتبات المطلوبة للـ WeasyPrint والخطوط والرسوميات
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpango1.0-dev \
    libpangoft2-1.0-0 \
    libcairo2 \
    libcairo2-dev \
    libffi-dev \
    libssl-dev \
    fonts-liberation \
    fonts-dejavu \
    fonts-liberation2 \
    fonts-noto \
    fonts-noto-cjk \
    fonts-noto-color-emoji \
    && rm -rf /var/lib/apt/lists/*

# Runtime Stage
FROM python:3.11-slim

# نسخ المكتبات المثبتة من مرحلة البناء
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpango1.0-dev \
    libpangoft2-1.0-0 \
    libcairo2 \
    libcairo2-dev \
    fonts-liberation \
    fonts-dejavu \
    fonts-liberation2 \
    fonts-noto \
    fonts-noto-color-emoji \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# نسخ ملفات المتطلبات
COPY requirements.txt .

# تثبيت المكتبات Python
RUN pip install --no-cache-dir -r requirements.txt

# نسخ كل ملفات المشروع
COPY app.py .
COPY document_engine.py .
COPY assets/ ./assets/
COPY brand-kit/ ./brand-kit/

# صلاحيات التنفيذ
RUN chmod +x app.py

# Expose المنفذ الافتراضي
EXPOSE 8000

# تشغيل التطبيق
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
