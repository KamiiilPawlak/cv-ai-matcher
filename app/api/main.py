from app.api.v1.routes.health import router as health_router
from fastapi import FastAPI

app = FastAPI()

app.include_router(health_router, prefix="/app/api/v1")

