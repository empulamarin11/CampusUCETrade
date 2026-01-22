# app/infrastructure/repositories.py
from sqlalchemy.orm import Session

from app.domain.models import Reputation
from app.domain.ports import ReputationRepositoryPort


class SqlAlchemyReputationRepository(ReputationRepositoryPort):
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, user_email: str):
        return (
            self.db.query(Reputation)
            .filter(Reputation.user_email == user_email.lower())
            .one_or_none()
        )

    def save(self, rep: Reputation) -> Reputation:
        self.db.add(rep)
        self.db.commit()
        self.db.refresh(rep)
        return rep
