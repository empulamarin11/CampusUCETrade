# app/config.py
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Service (for gateway consistency)
    service_root_path: str = os.getenv("SERVICE_ROOT_PATH", "/delivery")

    # JWT
    jwt_secret: str = os.getenv("JWT_SECRET", "dev_jwt_secret_key")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")

    # MQTT
    mqtt_host: str = os.getenv("MQTT_HOST", "mqtt")
    mqtt_port: int = int(os.getenv("MQTT_PORT", "1883"))
    mqtt_username: str = os.getenv("MQTT_USERNAME", "")
    mqtt_password: str = os.getenv("MQTT_PASSWORD", "")
    mqtt_client_id: str = os.getenv("MQTT_CLIENT_ID", "delivery-service")

    # Topics (MQTT contract)
    topic_create: str = os.getenv("TOPIC_CREATE", "campus/delivery/create")
    topic_confirm: str = os.getenv("TOPIC_CONFIRM", "campus/delivery/confirm")
    topic_delivered: str = os.getenv("TOPIC_DELIVERED", "campus/delivery/delivered")

    class Config:
        env_file = ".env"


settings = Settings()
