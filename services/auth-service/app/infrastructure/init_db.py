from app.infrastructure.db import engine, Base
from app.infrastructure import models  # noqa: F401

def init_db() -> None:
    Base.metadata.create_all(bind=engine)