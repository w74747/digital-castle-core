FROM python:3.11-slim

# تعيين متغيرات البيئة
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# تثبيت المكتبات النظام المطلوبة للرسوميات والخطوط
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf2.0-0 \
    shared-mime-info \
    fonts-dejavu \
    fonts-liberation \
    fonts-noto \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# تعيين مجلد العمل
WORKDIR /app

# نسخ ملفات المتطلبات
COPY requirements.txt .

# تثبيت المكتبات Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# نسخ ملفات المشروع
COPY . .

# إنشاء المجلدات المطلوبة
RUN mkdir -p logs assets brand-kit/.spec-kit docs agents

# تعريض المنفذ
EXPOSE 8000

# أمر التشغيل
CMD ["python", "app.py"]
