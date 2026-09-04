---
description: 사이트 전체 점검 — 제목·메타·H2 구조·내부 링크·광고 배치·기본 속도
---
$ARGUMENTS
`python scripts/site_audit.py` 실행(사이트맵 기준). analyst(D)가 결과 해석: 메타 없음·중복, H1 여러 개, 질문형 소제목 비율, 내부 링크 없는 글, alt 누락. builder(D) 광고 배치 점검 항목. → `content/reports/audit-YYYY-MM-DD.md`. 보고: 문제 상위 5개와 각각 /fix 지시문.
