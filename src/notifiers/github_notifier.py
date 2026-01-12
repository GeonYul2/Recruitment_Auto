"""
GitHub Issue 알림 서비스

단일 책임: 매칭 결과를 Issue 코멘트로 전달
"""
from datetime import datetime
from typing import Dict, List

from src.core.interfaces import NotifierProtocol
from src.models.job import JobPosting
from src.models.match import MatchResult
from src.services.github_service import GitHubService


class GitHubNotifier(NotifierProtocol):
    """GitHub Issue 코멘트 알림"""

    def __init__(self, github_service: GitHubService):
        self._github = github_service

    async def notify(
        self,
        recipient: str,  # Issue number
        subject: str,
        content: str
    ) -> bool:
        """Issue에 코멘트 작성"""
        issue_number = int(recipient)
        return await self._github.post_comment(issue_number, content)

    def format_match_comment(
        self,
        matches: List[MatchResult],
        jobs_map: Dict[str, JobPosting],
    ) -> str:
        """매칭 결과를 마크다운 코멘트로 포맷"""
        today = datetime.now().strftime("%Y-%m-%d")

        if not matches:
            return f"""## 매칭 결과 ({today})

오늘 새로 매칭된 공고가 없습니다.

---
*자동 생성됨 by Recruitment Auto*
"""

        lines = [
            f"## 새로운 매칭 공고 ({today})",
            "",
            f"총 **{len(matches)}건**의 공고가 프로필과 매칭되었습니다.",
            "",
            "| 회사 | 포지션 | 매칭률 | 마감 | 매칭 기술 |",
            "|------|--------|--------|------|-----------|",
        ]

        for match in matches:
            job = jobs_map.get(match.job_id)
            if not job:
                continue

            # 회사명 truncate
            company = job.company_name
            if len(company) > 10:
                company = company[:10] + "..."

            # 포지션명 truncate
            title = job.title
            if len(title) > 20:
                title = title[:20] + "..."

            deadline = job.deadline_text or "상시"
            matched_skills = ", ".join(match.matched_skills[:3]) or "-"

            lines.append(
                f"| [{company}]({job.source_url}) | {title} | "
                f"**{match.total_score:.0f}%** | {deadline} | {matched_skills} |"
            )

        lines.extend([
            "",
            "<details>",
            "<summary>매칭 기준 안내</summary>",
            "",
            "- 직무 카테고리: 30점",
            "- 경력 조건: 20점",
            "- 위치 조건: 10점",
            "- 스킬/설명 유사도: 40점",
            "",
            "</details>",
            "",
            "---",
            "*자동 생성됨 by [Recruitment Auto](https://1916571-alt.github.io/Recruitment_Auto/)*",
        ])

        return "\n".join(lines)
