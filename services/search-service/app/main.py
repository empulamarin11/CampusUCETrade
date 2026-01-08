import os
from fastapi import FastAPI
from app.routers import router

SERVICE_NAME = "search-service"

def create_app() -> FastAPI:
    root_path = os.getenv("SERVICE_ROOT_PATH", "")

    app = FastAPI(
        title=f"CampusUCETrade - {SERVICE_NAME}",
        version="0.1.0",
        root_path=root_path,
        root_path_in_servers=True,
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    app.include_router(router)

    return app

app = create_app()
