# 중복 콘텐츠 정리 가이드
**작성: 2026-10-08**

---

## 작업 순서: 쉬운 것부터

각 쌍마다 **남길 글** 하나, **삭제할 글** 하나.
삭제 = 워드프레스에서 **휴지통**으로 이동 (완전 삭제 아님).
리다이렉트 = Rank Math → 리다이렉션 → 301 추가.

---

### 1번. 백김치 (가장 간단 — 노출 차이 큼)

| | URL | 노출 | 클릭 |
|---|---|---|---|
| **남김** | `/white-kimchi-recipe-clean-flavor-without-chili/` | 144 | 1 |
| **삭제** | `/baek-kimchi-recipe-white-kimchi-without-chili/` | 5 | 1 |

**할 일:**
1. 두 글 열어서 비교 — 5짜리에만 있는 내용이 있으면 144짜리에 복사
2. `/baek-kimchi-recipe-white-kimchi-without-chili/` → 휴지통
3. Rank Math → 리다이렉션:
   - 원본 URL: `/baek-kimchi-recipe-white-kimchi-without-chili/`
   - 대상 URL: `/white-kimchi-recipe-clean-flavor-without-chili/`
   - 유형: 301

---

### 2번. 김치 종류 (슬러그에 -2 붙은 중복)

| | URL | 노출 | 클릭 |
|---|---|---|---|
| **남김** | `/kimchi-varieties-by-region-200-types-explained/` | 55 | 2 |
| **삭제** | `/kimchi-varieties-by-region-200-types-explained-2/` | 13 | 2 |

**할 일:**
1. -2 글은 자동발행이 만든 사본일 가능성 높음. 내용 확인
2. `/kimchi-varieties-by-region-200-types-explained-2/` → 휴지통
3. Rank Math → 리다이렉션:
   - 원본: `/kimchi-varieties-by-region-200-types-explained-2/`
   - 대상: `/kimchi-varieties-by-region-200-types-explained/`
   - 유형: 301

---

### 3번. 깍두기

| | URL | 노출 | 클릭 |
|---|---|---|---|
| **남김** | `/kkakdugi-golden-recipe-the-secret-to-that-perfect-crunch/` | 35 | 0 |
| **삭제** | `/kkakdugi-recipe-the-secret-to-perfect-crunch/` | 26 | 0 |

**할 일:**
1. 26짜리에만 있는 좋은 내용 → 35짜리로 이동
2. `/kkakdugi-recipe-the-secret-to-perfect-crunch/` → 휴지통
3. Rank Math → 리다이렉션:
   - 원본: `/kkakdugi-recipe-the-secret-to-perfect-crunch/`
   - 대상: `/kkakdugi-golden-recipe-the-secret-to-that-perfect-crunch/`
   - 유형: 301

---

### 4번. 한국 간장 가이드

| | URL | 노출 | 클릭 |
|---|---|---|---|
| **남김** | `/the-complete-guide-to-korean-soy-sauce-types/` | 54 | 0 |
| **삭제** | `/korean-soy-sauce-a-complete-guide-by-type/` | 37 | 0 |

**할 일:**
1. 37짜리에만 있는 내용 → 54짜리로 이동
2. `/korean-soy-sauce-a-complete-guide-by-type/` → 휴지통
3. Rank Math → 리다이렉션:
   - 원본: `/korean-soy-sauce-a-complete-guide-by-type/`
   - 대상: `/the-complete-guide-to-korean-soy-sauce-types/`
   - 유형: 301

---

### 5번. 발효 식품 보관법 (가장 중요 — 노출 합계 456)

| | URL | 노출 | 클릭 |
|---|---|---|---|
| **남김** | `/how-to-store-fermented-foods-the-right-way/` | 277 | 0 |
| **삭제** | `/how-to-store-korean-fermented-foods-properly/` | 179 | 0 |

**할 일:**
1. **이 쌍은 합치는 게 특히 중요.** 노출 합계 456인데 클릭 0 — 합치면 순위가 확 올라갈 가능성
2. 179짜리 글의 내용 중 277짜리에 없는 것 → 전부 복사
3. `/how-to-store-korean-fermented-foods-properly/` → 휴지통
4. Rank Math → 리다이렉션:
   - 원본: `/how-to-store-korean-fermented-foods-properly/`
   - 대상: `/how-to-store-fermented-foods-the-right-way/`
   - 유형: 301

---

### 6번. 김치찌개 (확인 필요)

| | URL | 노출 | 클릭 |
|---|---|---|---|
| **확인** | 원본 김치찌개 글 (슬러그에 -2 없는 버전) | ? | ? |
| **삭제** | `/kimchi-jjigae-the-perfect-fermented-stew-recipe-2/` | 28 | 0 |

**할 일:**
1. wp-admin → 글 목록에서 "kimchi jjigae" 검색
2. -2 없는 원본이 있으면: -2 삭제 + 원본으로 301 리다이렉트
3. 원본이 없으면 (삭제됨): -2 글의 슬러그를 `-2` 제거한 것으로 변경

---

## Rank Math 리다이렉션 설정 방법

1. WordPress 관리자 → **Rank Math** → **리다이렉션**
2. **새로 추가** 클릭
3. 소스 URL: 위에 적은 **원본 URL** (앞의 `/` 부터)
4. 대상 URL: 위에 적은 **대상 URL**
5. 리다이렉션 유형: **301 영구 이동**
6. 저장

총 5-6개 리다이렉트. 한 번에 30분이면 끝남.

---

## 완료 후 할 것

- [ ] Google Search Console → URL 검사 → 삭제한 URL 입력 → "인덱싱 요청" (구글이 빨리 반영하게)
- [ ] 남긴 글도 URL 검사 → "인덱싱 요청"
- [ ] 2-3주 후 GSC에서 노출·클릭 변화 확인
