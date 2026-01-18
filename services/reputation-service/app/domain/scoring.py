# app/domain/scoring.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List

from app.domain.ports import RatingInput, ScoringRulePort


@dataclass
class ClampScoreRule(ScoringRulePort):
    min_score: int = 0
    max_score: int = 100

    def apply(self, current_score: int, rating: RatingInput) -> int:
        if current_score < self.min_score:
            return self.min_score
        if current_score > self.max_score:
            return self.max_score
        return current_score


class BasicStarToPointsRule(ScoringRulePort):
    """
    MVP:
    - rating.points is 1..5
    - adds points to a running total which later becomes a score 0..100
    This rule returns a NEW score estimate for simplicity.
    """
    def apply(self, current_score: int, rating: RatingInput) -> int:
        # Simple mapping: 1..5 => +0..+20 impact, then clamp later
        impact = (rating.points - 1) * 5  # 1=>0, 5=>20
        return current_score + impact


class ScoringEngine:
    def __init__(self, rules: List[ScoringRulePort]):
        self.rules = rules

    def calculate_new_score(self, current_score: int, rating: RatingInput) -> int:
        score = current_score
        for rule in self.rules:
            score = rule.apply(score, rating)
        return score


def default_engine() -> ScoringEngine:
    return ScoringEngine(
        rules=[
            BasicStarToPointsRule(),
            ClampScoreRule(0, 100),
        ]
    )
