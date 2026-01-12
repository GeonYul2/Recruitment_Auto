"""
매칭 결과 모델

프로필과 채용 공고 간의 매칭 결과를 정의합니다.
"""
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    """매칭 점수 상세"""
    category_score: float = Field(0.0, description="직무 카테고리 점수 (0-30)")
    experience_score: float = Field(0.0, description="경력 조건 점수 (0-20)")
    location_score: float = Field(0.0, description="위치 조건 점수 (0-10)")
    embedding_score: float = Field(0.0, description="임베딩 유사도 점수 (0-40)")


class MatchResult(BaseModel):
    """매칭 결과"""
    profile_id: str = Field(..., description="프로필 Issue ID")
    job_id: str = Field(..., description="채용 공고 ID")

    # 점수
    total_score: float = Field(..., description="총점 (0-100)")
    score_breakdown: ScoreBreakdown = Field(
        default_factory=ScoreBreakdown,
        description="점수 상세"
    )

    # 매칭 분석
    matched_skills: List[str] = Field(default_factory=list, description="매칭된 기술")
    missing_skills: List[str] = Field(default_factory=list, description="부족한 기술")

    # 메타
    matched_at: datetime = Field(default_factory=datetime.now)


class ProfileMatchSummary(BaseModel):
    """프로필별 매칭 요약 (Issue 코멘트용)"""
    profile_id: str
    profile_username: str
    match_date: datetime
    matches: List[MatchResult]
    new_matches_count: int = Field(0, description="신규 매칭 수")
