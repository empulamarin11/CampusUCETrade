# app/main.py
import os
import logging
import threading
from fastapi import FastAPI
from app.api import router as api_router

from app.config import settings
from app.db import Base, engine
from app.mqtt_client import build_mqtt_client

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    
    title="Delivery-Service",
    root_path=settings.service_root_path,  # consistencia con gateway, aunque el core sea MQTT
    root_path_in_servers=True,
    docs_url="/docs",
    openapi_url="/openapi.json",
)
app.include_router(api_router)
_mqtt_client = None


@app.on_event("startup")
def startup():
    # MVP: create tables on startup
    if os.getenv("TESTING") != "1":
        Base.metadata.create_all(bind=engine)

    # MQTT client loop in background
    global _mqtt_client
    _mqtt_client = build_mqtt_client()
    _mqtt_client.connect(settings.mqtt_host, settings.mqtt_port, keepalive=60)

    t = threading.Thread(target=_mqtt_client.loop_forever, daemon=True)
    t.start()


@app.get("/health")
def health():
    return {"status": "ok", "service": "delivery-service", "protocol": "mqtt"}
