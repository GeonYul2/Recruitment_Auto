"""
GitHub API 연동 서비스

단일 책임: GitHub Issue 파싱 및 코멘트 작성
"""
import os
import re
from datetime import datetime
from typing import List, Optional

import aiohttp
from loguru import logger

from src.models.profile import Profile, JobCategory


# 직무 카테고리 매핑
JOB_CATEGORY_MAP = {
    "데이터 분석": JobCategory.DATA,
    "백엔드 개발": JobCategory.BACKEND,
    "프론트엔드 개발": JobCategory.FRONTEND,
    "풀스택 개발": JobCategory.FULLSTACK,
    "기획/PM": JobCategory.PM,
    "디자인": JobCategory.DESIGN,
}


class GitHubService:
    """GitHub API 서비스"""

    def __init__(
        self,
        token: Optional[str] = None,
        repo: str = "1916571-alt/Recruitment_Auto"
    ):
        self._token = token or os.environ.get("GITHUB_TOKEN")
        self._repo = repo
        self._api_base = "https://api.github.com"

    @property
    def _headers(self) -> dict:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    async def get_profile_issues(self) -> List[dict]:
        """profile 라벨이 붙은 Issue 목록 조회"""
        url = f"{self._api_base}/repos/{self._repo}/issues"
        params = {
            "labels": "profile",
            "state": "open",
            "per_page": 100,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, headers=self._headers, params=params
            ) as resp:
                if resp.status != 200:
                    logger.error(f"GitHub API error: {resp.status}")
                    return []
                return await resp.json()

    def parse_issue_to_profile(self, issue: dict) -> Optional[Profile]:
        """Issue 본문을 Profile 객체로 파싱"""
        try:
            body = issue.get("body", "")
            issue_number = issue["number"]
            issue_url = issue["html_url"]

            # 섹션 파싱
            data = self._parse_issue_body(body)

            if not data.get("github_username"):
                logger.warning(f"Issue #{issue_number}: github_username 없음")
                return None

            # 스킬 파싱 (줄바꿈으로 분리)
            skills = self._parse_multiline(data.get("skills", ""))
            certifications = self._parse_multiline(data.get("certifications", ""))
            locations = self._parse_comma_separated(data.get("preferred_location", ""))

            # 직무 카테고리 매핑
            job_category = JOB_CATEGORY_MAP.get(
                data.get("job_category", ""),
                JobCategory.DATA
            )

            # 경력 파싱
            try:
                experience_years = int(data.get("experience_years", 0))
            except ValueError:
                experience_years = 0

            return Profile(
                id=str(issue_number),
                github_username=data["github_username"],
                email=data.get("email") or None,
                job_category=job_category,
                experience_years=experience_years,
                preferred_locations=locations,
                skills=skills,
                certifications=certifications,
                introduction=data.get("introduction") or None,
                issue_url=issue_url,
                created_at=datetime.fromisoformat(
                    issue["created_at"].replace("Z", "+00:00")
                ),
            )
        except Exception as e:
            logger.error(f"Profile parsing error: {e}")
            return None

    def _parse_issue_body(self, body: str) -> dict:
        """Issue 본문 파싱 (GitHub Issue 템플릿 형식)"""
        result = {}

        # 패턴: ### 라벨\n\n값
        pattern = r"### (.+?)\n\n(.*?)(?=\n### |\Z)"
        matches = re.findall(pattern, body, re.DOTALL)

        for label, value in matches:
            key = self._label_to_key(label.strip())
            result[key] = value.strip()

        return result

    def _label_to_key(self, label: str) -> str:
        """라벨을 키로 변환"""
        mapping = {
            "GitHub 사용자명": "github_username",
            "희망 직무": "job_category",
            "경력 (년)": "experience_years",
            "보유 기술": "skills",
            "자격증 (선택)": "certifications",
            "희망 근무지": "preferred_location",
            "이메일 (뉴스레터용, 선택)": "email",
            "간단한 자기소개 (선택)": "introduction",
        }
        return mapping.get(label, label.lower().replace(" ", "_"))

    def _parse_multiline(self, text: str) -> List[str]:
        """줄바꿈으로 구분된 텍스트 파싱"""
        if not text:
            return []
        lines = [line.strip().lstrip("- ") for line in text.split("\n")]
        return [line for line in lines if line]

    def _parse_comma_separated(self, text: str) -> List[str]:
        """쉼표로 구분된 텍스트 파싱"""
        if not text:
            return []
        items = [item.strip() for item in text.split(",")]
        return [item for item in items if item]

    async def post_comment(self, issue_number: int, body: str) -> bool:
        """Issue에 코멘트 작성"""
        if not self._token:
            logger.warning("GITHUB_TOKEN이 설정되지 않아 코멘트를 작성할 수 없습니다")
            return False

        url = f"{self._api_base}/repos/{self._repo}/issues/{issue_number}/comments"

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=self._headers,
                json={"body": body}
            ) as resp:
                if resp.status == 201:
                    logger.info(f"Comment posted to issue #{issue_number}")
                    return True
                else:
                    error_text = await resp.text()
                    logger.error(f"Failed to post comment: {resp.status} - {error_text}")
                    return False
