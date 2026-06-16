from fastapi import FastAPI
from app.api.health import router

app = FastAPI(
    title="MedGraph AI",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "message": "MedGraph AI Backend Running"
    }

app.include_router(router)