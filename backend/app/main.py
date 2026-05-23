from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict

from fastapi import FastAPI
from loguru import logger

from app.api.v1.router import api_router
from app.core.logger import setup_logging  # type: ignore

from .db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Uruchomienie aplikacji..")
    init_db()
    yield
    print("Zamykanie aplikacji..")


setup_logging()


app = FastAPI(title="CV AI Matcher", lifespan=lifespan)


app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root() -> Dict[str, str]:
    return {"message": "docker :D"}


logger.info("Progam został uruchomiony.....")
