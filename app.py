from fastapi import FastAPI
app = FastAPI(title="Digital Castle")
@app.get("/")
def root():
    return {"message": "🏰 Digital Castle Online"}
@app.get("/health")
def health():
    return {"status": "ok"}
