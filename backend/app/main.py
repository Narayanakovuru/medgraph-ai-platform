from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.health import router as health_router
from app.api.users import router as users_router
from app.api.graph import router as graph_router
from app.core.database import engine
from app.models.base import Base
# Make sure to import all models so Base has them registered before create_all
import app.models

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MedGraph AI",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "MedGraph AI Backend Running"
    }

app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(users_router, prefix="/api/users", tags=["users"])
app.include_router(graph_router, prefix="/api/graph", tags=["graph"])