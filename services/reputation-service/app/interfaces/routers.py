# app/interfaces/routers.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.interfaces.auth import get_current_email
from app.application.dtos import RateUserIn, ReputationOut
from app.application.use_cases import GetReputationUseCase, RateUserUseCase
from app.infrastructure.repositories import SqlAlchemyReputationRepository

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "service": "reputation-service", "protocol": "rest"}


@router.get("/reputation/{user_email}", response_model=ReputationOut)
def get_reputation(
    user_email: str,
    db: Session = Depends(get_db),
    _email: str = Depends(get_current_email),
):
    repo = SqlAlchemyReputationRepository(db)
    uc = GetReputationUseCase(repo)
    rep = uc.execute(user_email=user_email)
    return ReputationOut(user_email=rep.user_email, score=rep.score, ratings_count=rep.ratings_count)


@router.post("/reputation/rate", response_model=ReputationOut)
def rate_user(
    body: RateUserIn,
    db: Session = Depends(get_db),
    _email: str = Depends(get_current_email),
):
    repo = SqlAlchemyReputationRepository(db)
    uc = RateUserUseCase(repo)
    rep = uc.execute(user_email=body.user_email, points=body.points)
    return ReputationOut(user_email=rep.user_email, score=rep.score, ratings_count=rep.ratings_count)
