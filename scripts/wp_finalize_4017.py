#!/usr/bin/env python3
"""
Kimchi Complete Guide (ID 4017) 최종 마무리:
1. 내부 링크 8개를 실제 URL로 연결
2. 슬러그 설정 (kimchi-complete-guide)
3. 카테고리·태그 설정
4. Rank Math 메타 디스크립션 설정

실행: python scripts/wp_finalize_4017.py
"""
import json, os, re, sys
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(ROOT, "secrets", "wp.json")
c = json.load(open(CFG, encoding="utf-8"))
c["url"] = c["url"].rstrip("/")
auth = (c["user"], c["app_password"])
api = c["url"] + "/wp-json/wp/v2"

POST_ID = 4017

# --- 1. 기존 글 URL 찾기 ---
print("기존 글 URL 검색 중...")

# 내부 링크 대상 글 제목 → 검색 키워드
link_targets = [
    ("Korean Fermented Foods Explained", "Korean Fermented Foods Explained"),
    ("Best Probiotic Foods", "Best Probiotic Foods"),
    ("Salt and Fermentation", "Salt and Fermentation"),
    ("Pa Kimchi", "Pa Kimchi"),
    ("Mukeunji", "Mukeunji"),
    ("How to Store Fermented Foods the Right Way", "How to Store Fermented Foods"),
    ("Fermentation Molds", "Fermentation Molds"),
    ("Probiotics vs. Postbiotics", "Probiotics vs. Postbiotics"),
]

found_urls = {}
for title, search_q in link_targets:
    r = requests.get(api + "/posts", params={
        "search": search_q,
        "per_page": 5,
        "_fields": "id,title,link,slug",
        "status": "publish",
    }, auth=auth, timeout=20)
    if r.ok and r.json():
        post = r.json()[0]
        found_urls[title] = post["link"]
        print(f"  OK: {title} → {post['link']}")
    else:
        print(f"  !! 못 찾음: {title}")

# --- 2. 포스트 content 가져오기 (raw) ---
print(f"\n포스트 {POST_ID} 내용 가져오는 중...")
r = requests.get(api + f"/posts/{POST_ID}", params={
    "context": "edit",
    "_fields": "content",
}, auth=auth, timeout=20)
if not r.ok:
    print(f"포스트 읽기 실패: {r.status_code} {r.text[:200]}")
    sys.exit(1)

content = r.json()["content"]["raw"]
original_len = len(content)

# --- 3. 내부 링크 삽입 ---
# 본문에서 *Title* 또는 <em>Title</em> 패턴을 <a href="url">Title</a>로 변환
link_count = 0

for title, url in found_urls.items():
    pattern = re.compile(
        r'<em>([^<]*?' + re.escape(title) + r'[^<]*?)</em>',
        re.IGNORECASE
    )
    matches = pattern.findall(content)
    link_count += len(matches)
    content = pattern.sub(
        lambda m: f'<a href="{url}">{m.group(1)}</a>',
        content
    )

print(f"\n내부 링크 {link_count}개 삽입 완료")

# --- 4. 카테고리 찾기/만들기 ---
print("\n카테고리 설정 중...")
cat_ids = []
for cat_name in ["Fermentation Science"]:
    r = requests.get(api + "/categories", params={
        "search": cat_name,
        "_fields": "id,name",
    }, auth=auth, timeout=20)
    if r.ok and r.json():
        cat_ids.append(r.json()[0]["id"])
        print(f"  카테고리 찾음: {cat_name} (ID {r.json()[0]['id']})")
    else:
        # 카테고리 생성
        r2 = requests.post(api + "/categories", auth=auth,
                          json={"name": cat_name}, timeout=20)
        if r2.ok:
            cat_ids.append(r2.json()["id"])
            print(f"  카테고리 생성: {cat_name} (ID {r2.json()['id']})")
        else:
            print(f"  !! 카테고리 실패: {cat_name}")

# --- 5. 태그 찾기/만들기 ---
print("\n태그 설정 중...")
tag_ids = []
tag_names = ["kimchi", "fermentation", "korean food", "lactic acid bacteria", "probiotics", "fermented vegetables"]
for tag_name in tag_names:
    r = requests.get(api + "/tags", params={
        "search": tag_name,
        "_fields": "id,name",
    }, auth=auth, timeout=20)
    if r.ok and r.json():
        # 정확히 일치하는 것 찾기
        exact = [t for t in r.json() if t["name"].lower() == tag_name.lower()]
        if exact:
            tag_ids.append(exact[0]["id"])
            print(f"  태그 찾음: {tag_name} (ID {exact[0]['id']})")
            continue
    # 생성
    r2 = requests.post(api + "/tags", auth=auth,
                      json={"name": tag_name}, timeout=20)
    if r2.ok:
        tag_ids.append(r2.json()["id"])
        print(f"  태그 생성: {tag_name} (ID {r2.json()['id']})")
    else:
        print(f"  !! 태그 실패: {tag_name}")

# --- 6. 메타 디스크립션 (Rank Math) ---
meta_desc = "Kimchi is Korea's iconic fermented vegetable dish. Discover its history, fermentation science, varieties, nutrition, potential health effects, and proper storage."

# --- 7. 포스트 업데이트 ---
print(f"\n포스트 {POST_ID} 업데이트 중...")
update_data = {
    "content": content,
    "slug": "kimchi-complete-guide",
    "categories": cat_ids,
    "tags": tag_ids,
}

r = requests.post(api + f"/posts/{POST_ID}", auth=auth,
                  json=update_data, timeout=30)
if r.ok:
    print(f"포스트 업데이트 완료!")
    print(f"  슬러그: kimchi-complete-guide")
    print(f"  카테고리: {cat_ids}")
    print(f"  태그: {tag_ids}")
    print(f"  내부 링크: {link_count}개")
else:
    print(f"업데이트 실패: {r.status_code} {r.text[:300]}")
    sys.exit(1)

# --- 8. Rank Math 메타 (커스텀 필드) ---
# Rank Math는 _yoast_wpseo_metadesc 또는 rank_math_description 메타키 사용
print("\nRank Math 메타 디스크립션 설정 시도...")
r = requests.post(api + f"/posts/{POST_ID}", auth=auth,
                  json={"meta": {"rank_math_description": meta_desc,
                                 "rank_math_focus_keyword": "kimchi"}},
                  timeout=20)
if r.ok:
    print(f"  메타 디스크립션 설정 완료")
else:
    print(f"  메타 설정 실패 (수동으로 Rank Math에서 설정하세요): {r.status_code}")

print(f"\n완료! 편집: {c['url']}/wp-admin/post.php?post={POST_ID}&action=edit")
print("미리보기 확인 후 '발행' 버튼을 누르세요.")
