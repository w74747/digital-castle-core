# استخدام صورة Playwright الرسمية المجهزة بكافة متصفحات ومكتبات النظام والخطوط
FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

WORKDIR /app

# تثبيت متطلبات بايثون
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ ملفات المشروع
COPY . .

# أمر تشغيل البوت
CMD ["python", "main.py"]
