from typing import Dict

from fastapi import FastAPI

from app.api.v1.routes import health, ingestion

app = FastAPI(title="CV AI Matcher")


app.include_router(health.router, prefix="/api/v1", tags=["system"])
app.include_router(ingestion.router, prefix="/api/v1", tags=["Ingestion"])


@app.get("/")
def root() -> Dict[str, str]:
    return {"message": "docker :D"}
