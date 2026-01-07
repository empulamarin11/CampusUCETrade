from fastapi import FastAPI
from app.routers import router

app = FastAPI(
    title="CampusUCETrade - auth-service",
    version="0.1.0",
    root_path="/auth",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.include_router(router)
