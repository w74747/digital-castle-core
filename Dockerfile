FROM python:3.11-slim

# تثبيت المكتبات الرسومية والخطوط المطلوبة لـ WeasyPrint
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    fonts-cairo \
    fonts-noto \
    fonts-noto-cjk \
    fonts-noto-color-emoji \
    libffi-dev \
    libssl-dev \
    xfonts-75dpi \
    xfonts-96dpi \
    && rm -rf /var/lib/apt/lists/*

# تثبيت الخطوط العربية والإنجليزية
RUN apt-get update && apt-get install -y \
    fonts-liberation \
    fonts-dejavu \
    ttf-mscorefonts-installer \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# نسخ requirements وتثبيت الـ Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ ملفات التطبيق
COPY . .

# الملفات والأصول
RUN mkdir -p assets brand-kit/templates

# تشغيل التطبيق
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
