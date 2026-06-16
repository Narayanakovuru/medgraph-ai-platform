from app.core.database import SessionLocal
from app.core.neo4j_client import neo4j_client

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_neo4j_session():
    session = neo4j_client.get_session()
    try:
        yield session
    finally:
        session.close()
