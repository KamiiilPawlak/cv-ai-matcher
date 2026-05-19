from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict

from fastapi import FastAPI

from app.api.v1.routes import health, ingestion

from .db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Uruchomienie aplikacji..")
    init_db()
    yield
    print("Zamykanie aplikacji..")


app = FastAPI(title="CV AI Matcher", lifespan=lifespan)


app.include_router(health.router, prefix="/api/v1", tags=["system"])
app.include_router(ingestion.router, prefix="/api/v1", tags=["Ingestion"])


@app.get("/")
def root() -> Dict[str, str]:
    return {"message": "docker :D"}
