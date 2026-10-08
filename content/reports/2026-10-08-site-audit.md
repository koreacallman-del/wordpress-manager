# Fermentpedia.com 사이트 진단 및 활성화 계획
**진단일: 2026-10-08**

---

## 1. 현재 상태: 핵심 문제

### 구글 인덱싱 상황
- **사이트맵**: 59페이지 등록됨
- **실제 구글 검색 노출**: 3페이지만 확인됨
  - Kimchi and Weight Loss
  - Ganjang Gejang (간장게장)
  - Baek Kimchi Recipe (백김치)
- **"fermentpedia" 브랜드 검색**: 결과 0건 — 구글이 사이트를 거의 인식하지 못함
- **결론**: 59페이지 중 3페이지(5%)만 검색에 노출. 나머지 56페이지는 인덱싱 안 됐거나 저품질로 무시됨

### CTR(클릭률) 문제
사용자 말: "노출은 되는데 클릭이 없음"
- 2026년 구글 평균: AI Overview 있는 검색어는 CTR 60% 하락 (1위도 3.6%밖에 안 됨)
- 음식·건강 키워드는 AI Overview 비율 높음 → 제목·설명이 매력적이지 않으면 클릭 0

### 애드센스 승인 가능성
현재 상태로는 **거절 확률 높음**. 이유:

| 항목 | 요구 | 현재 상태 | 판정 |
|---|---|---|---|
| 고유 콘텐츠 15-20개+ | 필수 | 인덱싱 3개, 자동발행 콘텐츠 품질 미확인 | ❌ |
| About 페이지 | 필수 | 미확인 (없을 가능성 높음) | ❌ |
| Privacy Policy | 필수 | 미확인 | ❌ |
| Contact 페이지 | 필수 | 미확인 | ❌ |
| 면책조항 (YMYL) | 강력 권장 | 글 내부에만 있음, 별도 페이지 없음 | ⚠️ |
| 명확한 네비게이션 | 필수 | 미확인 | ⚠️ |
| 저자 E-E-A-T 신호 | 중요 | author slug 있지만 bio 미확인 | ⚠️ |
| 사이트맵/robots.txt | 기본 | 등록됨 | ✅ |
| 커스텀 도메인 | 기본 | fermentpedia.com | ✅ |

---

## 2. 즉시 해야 할 것 (1주 이내)

### A. 필수 페이지 4개 생성
애드센스 거절 사유 1위가 "필수 페이지 미비"

1. **About 페이지** — 누가 쓰는지, 왜 믿을 만한지
   - 식품 유통 30년 경력 명시
   - Hoon Kwak 저자 소개, 사진
   - 사이트 목적: 발효 식품의 과학적 정보 제공

2. **Privacy Policy** — 구글 애드센스 필수 요건
   - 쿠키 사용, 데이터 수집, 광고 네트워크 고지
   - WordPress 플러그인으로 자동 생성 가능 (WP AutoTerms 등)

3. **Contact 페이지** — 연락 폼 또는 이메일
   - WPForms Lite 등 무료 플러그인

4. **Disclaimer 페이지** — YMYL(건강) 사이트 필수
   - "정보 제공 목적, 의료 조언 아님" 별도 페이지

### B. 자동발행 콘텐츠 감사
**가장 긴급한 문제.** 주 3회 자동 발행(baehyo-auto-post)으로 올린 글 중 저품질·중복·얇은 콘텐츠가 있으면 애드센스 거절 + 구글 페널티 원인.

확인 작업:
- fermentpedia.com/wp-admin에서 전체 글 목록 확인
- 500자 미만 글, 이미지만 있는 글, 내용 중복 글 → **즉시 비공개 또는 삭제**
- 노인덱스 처리된 글 확인 (Rank Math에서 noindex 설정 여부)

### C. 구글 Search Console 확인
- **커버리지 보고서**: 인덱싱 안 된 56페이지의 이유 확인
  - "크롤링됨 - 현재 색인이 생성되지 않음" = 품질 부족
  - "발견됨 - 현재 색인이 생성되지 않음" = 크롤링 대기
  - "URL이 Google에 등록되어 있지 않음" = 사이트맵 문제
- **실적 보고서**: 노출 키워드별 CTR 확인 → 클릭 0인 키워드 목록

---

## 3. CTR(클릭률) 올리는 방법

### 제목 최적화
현재 제목 예시 vs 개선:

| 현재 | 문제 | 개선안 |
|---|---|---|
| Kimchi and Weight Loss: What the Science Actually Says | 길고 밋밋 | Does Kimchi Help You Lose Weight? Here's What 14 Studies Found |
| Ganjang Gejang: Korea's Soy-Marinated "Fermented Crab" Explained | 키워드 불분명 | Ganjang Gejang: Why Koreans Eat Raw Crab (And How It's Safe) |
| Baek Kimchi Recipe — Non-Spicy White Kimchi With Clean Fermented Flavor | 너무 김 | White Kimchi Recipe: Non-Spicy, Probiotic, Ready in 3 Days |

**규칙:**
- 60자 이내
- 숫자 넣기 (14 Studies, 3 Days, 5 Steps)
- 질문형 또는 "How/Why" 시작
- 괄호 활용: (Science-Based), (With Recipe), (2026 Guide)

### 메타 디스크립션
- 155자 이내
- 구체적 혜택 또는 결론 포함
- "Click here" 같은 유도 문구 금지
- 예: "Kimchi may support weight loss through gut bacteria changes. We reviewed 14 peer-reviewed studies. Here's what holds up — and what doesn't."

### Schema 마크업 (구조화 데이터)
Rank Math에서 설정 가능:

| 글 유형 | Schema | 효과 |
|---|---|---|
| 레시피 글 | Recipe schema | 별점, 조리시간, 칼로리 표시 → CTR 2-3배 |
| 정보 글 | Article + FAQ schema | FAQ 아코디언 표시 → SERP 면적 확대 |
| How-to 글 | HowTo schema | 단계별 표시 |

### 이미지 설정
```html
<meta name="robots" content="max-image-preview:large">
```
- Google Discover에서 큰 이미지 미리보기 → CTR 79% 증가 (Google 공식 케이스 스터디)
- Kadence 테마 또는 Rank Math에서 설정 가능

---

## 4. 콘텐츠 전략: 인덱싱 3개 → 30개로

### 현재 콘텐츠 구조 문제
- 글이 흩어져 있고 내부 링크 부족
- 주제 클러스터 없음 → 구글이 "이 사이트가 뭐 하는 곳인지" 판단 못함

### 콘텐츠 클러스터 설계

**Pillar 1: Kimchi (김치)** — 가장 검색량 높은 주제
- [Pillar] Complete Guide to Kimchi Fermentation
- [Cluster] Kimchi and Weight Loss (기존)
- [Cluster] White Kimchi Recipe (기존)
- [Cluster] How Long Does Kimchi Last?
- [Cluster] Kimchi vs Sauerkraut: What's the Difference?
- [Cluster] Best Probiotic Foods (작성 완료, 미발행)

**Pillar 2: Korean Fermented Pastes (장류)**
- [Pillar] Korean Fermented Pastes Explained: Doenjang, Gochujang, Ganjang
- [Cluster] Ganjang Gejang (기존)
- [Cluster] What Is Doenjang?
- [Cluster] Gochujang: How It's Made

**Pillar 3: Fermentation Science**
- [Pillar] How Fermentation Works: The Science Behind Every Jar
- [Cluster] Lactic Acid Bacteria Explained
- [Cluster] Is My Ferment Safe? Signs of Good vs Bad Fermentation

**Pillar 4: Health & Gut**
- [Pillar] Fermented Foods and Gut Health
- [Cluster] Best Probiotic Foods (작성 완료)
- [Cluster] Fermented Foods vs Probiotic Supplements

### 발행 우선순위 (애드센스 승인 전)
1. 필수 페이지 4개 (About, Privacy, Contact, Disclaimer)
2. Best Probiotic Foods 발행 (완성됨)
3. 기존 3개 글 제목·메타 최적화
4. Pillar 글 1개 (Kimchi Complete Guide)
5. 클러스터 글 3-5개 추가
→ **최소 15개 고품질 글 확보 후 애드센스 신청**

---

## 5. 기술 체크리스트

- [ ] robots.txt에 사이트맵 URL 명시 확인
- [ ] 사이트맵에 저품질 페이지 포함 여부 확인 → 제외
- [ ] Rank Math에서 각 글 SEO 점수 확인 (80점 이상 목표)
- [ ] max-image-preview:large 메타태그 추가
- [ ] 모든 이미지에 alt text 개별 작성
- [ ] 내부 링크: 모든 글에 최소 2-3개 내부 링크
- [ ] 모바일 반응형 확인 (Kadence 기본 지원이지만 확인)
- [ ] 페이지 속도: Google PageSpeed Insights에서 확인 (모바일 50점 이상)
- [ ] HTTPS 적용 확인

---

## 6. 액션 순서 요약

| 순서 | 작업 | 기간 | 누가 |
|---|---|---|---|
| 1 | 자동발행 글 감사 — 저품질 비공개 처리 | 1일 | 사용자 |
| 2 | GSC 커버리지 보고서 스크린샷 공유 | 1일 | 사용자 |
| 3 | 필수 페이지 4개 생성 (About/Privacy/Contact/Disclaimer) | 2-3일 | 같이 |
| 4 | 기존 3개 글 제목·메타 최적화 | 1일 | 같이 |
| 5 | Best Probiotic Foods 발행 | 1일 | 사용자 |
| 6 | Schema 마크업 설정 (Rank Math) | 1일 | 같이 |
| 7 | max-image-preview:large 추가 | 10분 | 같이 |
| 8 | Pillar 글 + 클러스터 글 5-7개 추가 작성 | 2-3주 | 같이 |
| 9 | 15개 이상 고품질 글 확보 후 애드센스 신청 | 3-4주 후 | 사용자 |
