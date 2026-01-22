# app/config.py
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    service_root_path: str = os.getenv("SERVICE_ROOT_PATH", "/traceability")

    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://campusuce:campusuce123@postgres:5432/campusuce",
    )

    # Kafka
    kafka_bootstrap: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    kafka_topic: str = os.getenv("KAFKA_TOPIC", "campus.audit")
    kafka_group_id: str = os.getenv("KAFKA_GROUP_ID", "traceability-service")

    # JWT (solo para proteger el GET /audit)
    jwt_secret: str = os.getenv("JWT_SECRET", "dev_jwt_secret_key")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")

    class Config:
        env_file = ".env"


settings = Settings()
