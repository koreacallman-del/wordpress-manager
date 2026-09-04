---
description: 워드프레스에 초안(draft)으로 업로드. 인자: 파일 경로
---
대상: $ARGUMENTS
`secrets/wp.json` 없으면 /setup의 연결 절차 안내 후 중단. `python scripts/wp_post.py <파일> --draft` 실행. 성공 시 워드프레스 관리자에서 초안을 여는 링크와 "미리보기 → 이미지 넣기 → 광고 위치 확인 → 발행" 절차 안내. plan.md 상태 "초안업로드". 발행은 사용자가 하고 `/done 발행함 <제목>`으로 알려달라고 안내.
