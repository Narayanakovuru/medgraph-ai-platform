from fastapi import APIRouter, Depends, HTTPException
from neo4j import Session
from app.api.deps import get_neo4j_session

router = APIRouter()

@router.get("/health")
def graph_health(session: Session = Depends(get_neo4j_session)):
    try:
        result = session.run("RETURN 1 AS number")
        record = result.single()
        return {"status": "Neo4j is reachable", "result": record["number"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
