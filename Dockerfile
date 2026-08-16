FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

RUN mkdir -p logs assets brand-kit/.spec-kit docs agents

EXPOSE 8000

CMD ["python", "app.py"]
