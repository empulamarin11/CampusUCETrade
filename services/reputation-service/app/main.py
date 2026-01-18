# app/main.py
from fastapi import FastAPI

from app.config import settings
from app.db import Base, engine
from app.interfaces.routers import router


app = FastAPI(
    title="Reputation-Service",
    root_path=settings.service_root_path,
    root_path_in_servers=True,
    docs_url="/docs",
    openapi_url="/openapi.json",
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


app.include_router(router)
