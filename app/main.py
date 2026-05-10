from typing import Dict

from fastapi import FastAPI

from app.api.v1.routes import health

app = FastAPI(title="CV AI Matcher")


app.include_router(health.router, prefix="/api/v1", tags=["system"])


@app.get("/")
def root() -> Dict[str, str]:
    return {"message": "Witamy w CV AI Matcher API"}
