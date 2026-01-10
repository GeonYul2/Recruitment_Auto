"""
채용 정보 수집 에이전트 설정
"""
from pathlib import Path
from typing import List
from pydantic import BaseModel


class FilterSettings(BaseModel):
    """필터링 설정"""
    # 직무 키워드 (OR 조건)
    job_keywords: List[str] = [
        "데이터 분석",
        "데이터분석",
        "Data Analyst",
        "Data Analysis",
        "데이터 사이언티스트",
        "Data Scientist",
        "BI 분석",
        "비즈니스 분석",
        "데이터 엔지니어",
        "Data Engineer",
        "머신러닝",
        "ML Engineer",
    ]

    # 제외 키워드 (타이틀에 이 키워드가 포함되면 제외)
    exclude_keywords: List[str] = [
        "시니어",
        "Senior",
        "팀장",
        "리드",
        "Lead",
        "Principal",
        "Staff",
        "Head",
    ]

    # 관심 기업 리스트 (데이터/AI 채용이 활발한 한국 기업)
    target_companies: List[str] = [
        # 빅테크/IT 대기업
        "네이버",
        "카카오",
        "라인",
        "쿠팡",
        "배달의민족",
        "우아한형제들",
        "토스",
        "비바리퍼블리카",
        "당근마켓",
        "당근",
        # 금융/핀테크
        "카카오뱅크",
        "케이뱅크",
        "토스뱅크",
        "신한은행",
        "KB국민은행",
        "하나은행",
        "삼성카드",
        "현대카드",
        # AI/데이터 전문
        "업스테이지",
        "뤼튼",
        "튜닙",
        "마인즈랩",
        "솔트룩스",
        "크래프톤",
        "엔씨소프트",
        "넷마블",
        # 이커머스/리테일
        "SSG",
        "신세계",
        "롯데이커머스",
        "11번가",
        "지마켓",
        "무신사",
        "오늘의집",
        "버킷플레이스",
        "마켓컬리",
        "컬리",
        # 모빌리티/물류
        "현대자동차",
        "기아",
        "현대모비스",
        "카카오모빌리티",
        "쏘카",
        "타다",
        # 헬스케어/바이오
        "뷰노",
        "루닛",
        "딥노이드",
        # 스타트업/유니콘
        "야놀자",
        "여기어때",
        "직방",
        "리멤버",
        "드라마앤컴퍼니",
        "원티드랩",
        "스푼라디오",
        "하이퍼커넥트",
        # 컨설팅/SI
        "삼성SDS",
        "LG CNS",
        "SK C&C",
        "NHN",
    ]


class CrawlerSettings(BaseModel):
    """크롤러 설정"""
    # 크롤링 간격 (분)
    crawl_interval_minutes: int = 60

    # 요청 간 대기 시간 (초)
    request_delay_seconds: float = 2.0

    # 타임아웃 (초)
    request_timeout: int = 30

    # User-Agent
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )


class DatabaseSettings(BaseModel):
    """데이터베이스 설정"""
    db_path: Path = Path("data/jobs.db")


class WebSettings(BaseModel):
    """웹 서버 설정"""
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True


class Settings(BaseModel):
    """전체 설정"""
    filter: FilterSettings = FilterSettings()
    crawler: CrawlerSettings = CrawlerSettings()
    database: DatabaseSettings = DatabaseSettings()
    web: WebSettings = WebSettings()

    # 프로젝트 루트 경로
    base_dir: Path = Path(__file__).parent.parent


# 전역 설정 인스턴스
settings = Settings()
