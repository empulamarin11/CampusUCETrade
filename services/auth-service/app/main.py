import os
from fastapi import FastAPI
from redis.asyncio import from_url as redis_from_url
from fastapi_limiter import FastAPILimiter
from app.infrastructure.init_db import init_db

from app.interfaces.routers import router



async def _rate_limit_identifier(request):
    # works behind gateway (x-forwarded-for) and local
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


app = FastAPI(
    title="CampusUCETrade - auth-service",
    version="0.2.0",
    root_path="/auth",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.include_router(router)


@app.on_event("startup")
async def startup():
    init_db()
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis = redis_from_url(redis_url, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis, identifier=_rate_limit_identifier)
