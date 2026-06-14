from fastapi import FastAPI

app = FastAPI(
    title="MedGraph AI",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "message": "MedGraph AI Backend Running"
    }