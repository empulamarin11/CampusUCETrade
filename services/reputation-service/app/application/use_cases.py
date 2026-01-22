# app/application/use_cases.py
from datetime import datetime

from app.domain.models import Reputation
from app.domain.ports import ReputationRepositoryPort, RatingInput
from app.domain.scoring import ScoringEngine, default_engine


class GetReputationUseCase:
    def __init__(self, repo: ReputationRepositoryPort):
        self.repo = repo

    def execute(self, user_email: str) -> Reputation:
        rep = self.repo.get_by_email(user_email.lower())
        if rep:
            return rep

        # If no record, create default
        rep = Reputation(
            user_email=user_email.lower(),
            score=0,
            ratings_count=0,
            total_points=0,
            updated_at=datetime.utcnow(),
        )
        return self.repo.save(rep)


class RateUserUseCase:
    def __init__(self, repo: ReputationRepositoryPort, engine: ScoringEngine | None = None):
        self.repo = repo
        self.engine = engine or default_engine()

    def execute(self, user_email: str, points: int) -> Reputation:
        rep = self.repo.get_by_email(user_email.lower())
        if not rep:
            rep = Reputation(
                user_email=user_email.lower(),
                score=0,
                ratings_count=0,
                total_points=0,
                updated_at=datetime.utcnow(),
            )

        rating = RatingInput(user_email=user_email.lower(), points=points)

        # Update aggregates
        rep.ratings_count += 1
        rep.total_points += points

        # Score uses engine (O/C)
        rep.score = self.engine.calculate_new_score(rep.score, rating)
        rep.updated_at = datetime.utcnow()

        return self.repo.save(rep)
