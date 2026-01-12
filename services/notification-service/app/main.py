import os
from fastapi import FastAPI

from app.routers import router
from app.db import Base, engine
from app.mq_consumer import start_consumer_thread

SERVICE_NAME = "notification-service"


def create_app() -> FastAPI:
    root_path = os.getenv("SERVICE_ROOT_PATH", "")

    app = FastAPI(
        title=f"CampusUCETrade - {SERVICE_NAME}",
        version="0.2.0",
        root_path=root_path,
        root_path_in_servers=True,
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    Base.metadata.create_all(bind=engine)

    @app.on_event("startup")
    def _startup() -> None:
        start_consumer_thread()

    app.include_router(router)
    return app


app = create_app()
