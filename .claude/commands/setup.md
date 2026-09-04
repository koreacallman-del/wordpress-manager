---
description: 첫 설정 — 사이트 정보·주제·언어·워드프레스 연결을 대화로
---
`skills/common/site.md`를 연다. 항목을 한 번에 하나씩, 초보자에게 말하듯 예시와 함께 묻는다. 워드프레스 REST API 연결은 원할 때만: 절차(워드프레스 관리자 → 사용자 → 프로필 → 응용 프로그램 비밀번호 생성)를 안내하고, 사용자명과 비밀번호를 받으면 `secrets/wp.json`에 `{"url":"...","user":"...","app_password":"..."}`로 저장하고 `python scripts/wp_post.py --test`로 연결 확인. 채우면 site.md 저장, "이제 /plan <주제> 로 시작할 수 있습니다" 안내.
