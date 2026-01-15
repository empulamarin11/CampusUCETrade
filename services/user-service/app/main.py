from fastapi import FastAPI
from app.interfaces.routers import router
from app.infrastructure.init_db import init_db

app = FastAPI(
    title="CampusUCETrade - user-service",
    version="0.1.0",
    root_path="/users",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.include_router(router)

@app.on_event("startup")
async def startup():
    init_db()