# Recruitment Auto - 채용 정보 자동 수집 & 매칭 에이전트

> 채용 공고를 자동 수집하고, GitHub Issue 프로필 기반으로 맞춤 공고를 추천하는 에이전트

## 대시보드

**https://1916571-alt.github.io/Recruitment_Auto/**

## 특징

- **자동 수집**: GitHub Actions가 매일 09:00 KST 자동 크롤링
- **프로필 매칭**: GitHub Issue로 프로필 등록 → 맞춤 공고 추천
- **무료 호스팅**: GitHub Pages로 서버 비용 없이 운영
- **다양한 직군**: 데이터, 백엔드, 프론트엔드, PM/기획
- **신입 전용**: 신입/경력무관/인턴/주니어 공고만 수집

## 자동화 파이프라인

```
GitHub Actions (매일 09:00 KST)
    ↓
1. crawl-to-json    : 채용 공고 수집 → data/jobs.json
    ↓
2. build-static     : 정적 사이트 생성 → docs/
    ↓
3. match-profiles   : 프로필-공고 매칭 → Issue 코멘트
    ↓
4. deploy           : GitHub Pages 배포
```

## 프로필 등록 방법

1. [Issues](../../issues) 탭에서 "New Issue" 클릭
2. "프로필 등록" 템플릿 선택
3. 정보 입력 후 제출
4. 매일 자동으로 맞춤 공고가 코멘트로 전달됨

### 프로필 형식

```markdown
### GitHub 사용자명
your-username

### 희망 직무
데이터 분석 / 백엔드 개발 / 프론트엔드 개발 / PM/기획

### 경력 (년)
0

### 보유 기술
Python
SQL
Pandas

### 희망 근무지
서울, 판교
```

job_keywords = [
    # 데이터 분석
    "데이터 분석", "Data Analyst", "데이터 사이언티스트", "DA", "DS",
]
```

## 대상 채용 사이트

| 사이트 | 상태 |
|--------|------|
| 사람인 | ✅ |
| 인디스워크 | ✅ |
```

## License

MIT - 개인 학습 및 정보 수집 목적으로 사용하세요.
