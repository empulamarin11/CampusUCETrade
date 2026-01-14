from fastapi import FastAPI
from app.routers import router
from app.db import engine
from app.models import User  # noqa: F401
from app.db import Base

app = FastAPI(
    title="CampusUCETrade - user-service",
    version="0.2.0",
    root_path="/users",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)

app.include_router(router)
