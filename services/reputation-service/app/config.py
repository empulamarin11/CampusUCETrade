# app/config.py
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    service_root_path: str = os.getenv("SERVICE_ROOT_PATH", "/reputation")

    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://campusuce:campusuce123@postgres:5432/campusuce",
    )

    jwt_secret: str = os.getenv("JWT_SECRET", "dev_jwt_secret_key")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")

    class Config:
        env_file = ".env"


settings = Settings()
