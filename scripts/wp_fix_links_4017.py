#!/usr/bin/env python3
"""
포스트 4017의 잘못된 내부 링크를 수정한다.
1단계: 전체 발행글 목록에서 정확한 제목 매칭으로 URL 찾기
2단계: 잘못 삽입된 <a> 태그를 제거하고 올바른 링크 재삽입

실행: python scripts/wp_fix_links_4017.py
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

# --- 1. 전체 발행글 가져오기 ---
print("전체 발행글 목록 가져오는 중...")
all_posts = []
page = 1
while True:
    r = requests.get(api + "/posts", params={
        "per_page": 100,
        "page": page,
        "status": "publish,draft",
        "_fields": "id,title,link,slug",
    }, auth=auth, timeout=30)
    if not r.ok:
        break
    batch = r.json()
    if not batch:
        break
    all_posts.extend(batch)
    print(f"  페이지 {page}: {len(batch)}개 (누적 {len(all_posts)})")
    if len(batch) < 100:
        break
    page += 1

print(f"  총 {len(all_posts)}개 글")

# --- 2. 제목으로 정확한 매칭 ---
# 찾아야 할 글 제목의 핵심 부분
targets = {
    "Korean Fermented Foods Explained": ["korean fermented foods explained"],
    "Best Probiotic Foods": ["best probiotic foods"],
    "Salt and Fermentation": ["salt and fermentation", "how sodium controls"],
    "Pa Kimchi": ["pa kimchi", "ferment green onions"],
    "Mukeunji": ["mukeunji", "aged kimchi"],
    "How to Store Fermented Foods the Right Way": ["how to store fermented foods"],
    "Fermentation Molds": ["fermentation molds"],
    "Probiotics vs. Postbiotics": ["probiotics vs. postbiotics", "probiotics vs postbiotics"],
}

found = {}
for label, keywords in targets.items():
    for post in all_posts:
        title_lower = post["title"]["rendered"].lower()
        if any(kw in title_lower for kw in keywords):
            found[label] = {
                "id": post["id"],
                "title": post["title"]["rendered"],
                "link": post["link"],
                "slug": post["slug"],
            }
            break

print("\n=== 매칭 결과 ===")
for label, info in found.items():
    print(f"  OK: {label}")
    print(f"      → ID {info['id']}: {info['title']}")
    print(f"      → {info['link']}")

not_found = set(targets.keys()) - set(found.keys())
if not_found:
    print(f"\n  !! 못 찾음: {not_found}")
    print("  이 글들은 수동으로 링크해야 합니다.")

# --- 3. 포스트 content 가져오기 ---
print(f"\n포스트 {POST_ID} 내용 가져오는 중...")
r = requests.get(api + f"/posts/{POST_ID}", params={
    "context": "edit",
    "_fields": "content",
}, auth=auth, timeout=20)
if not r.ok:
    print(f"읽기 실패: {r.status_code}")
    sys.exit(1)

content = r.json()["content"]["raw"]

# --- 4. 잘못된 링크 제거 (모든 <a> 태그를 <em>으로 되돌리기) ---
# 이전 스크립트가 <em>Title</em> → <a href="wrong">Title</a> 로 바꿨으므로
# 내부 링크로 삽입된 <a> 태그를 찾아서 <em>으로 복원
wrong_urls = [
    "baechu-kimchi-recipe",
    "sikhye-is-koreas-sweet-rice-drink",
    "fermented-vs-pickled",
]

def restore_wrong_links(content):
    # 잘못된 URL을 가진 <a> 태그를 <em>으로 복원
    count = 0
    for wrong in wrong_urls:
        pattern = re.compile(
            r'<a href="[^"]*' + re.escape(wrong) + r'[^"]*">([^<]+)</a>',
            re.IGNORECASE
        )
        matches = pattern.findall(content)
        count += len(matches)
        content = pattern.sub(r'<em>\1</em>', content)
    return content, count

content, restored = restore_wrong_links(content)
print(f"잘못된 링크 {restored}개 복원 (→ <em>)")

# --- 5. 올바른 링크 삽입 ---
link_count = 0

# 본문에서 찾을 패턴: 각 대상 글의 제목이 포함된 <em>...</em>
for label, info in found.items():
    url = info["link"]
    pattern = re.compile(
        r'<em>([^<]*?' + re.escape(label) + r'[^<]*?)</em>',
        re.IGNORECASE
    )
    matches = pattern.findall(content)
    link_count += len(matches)
    content = pattern.sub(
        lambda m, u=url: f'<a href="{u}">{m.group(1)}</a>',
        content
    )

print(f"올바른 링크 {link_count}개 삽입")

# --- 6. 업데이트 ---
print(f"\n포스트 {POST_ID} 업데이트 중...")
r = requests.post(api + f"/posts/{POST_ID}", auth=auth,
                  json={"content": content}, timeout=30)
if r.ok:
    print("업데이트 완료!")
else:
    print(f"실패: {r.status_code} {r.text[:300]}")
    sys.exit(1)

print(f"\n편집: {c['url']}/wp-admin/post.php?post={POST_ID}&action=edit")
print("미리보기에서 내부 링크가 올바른 글로 연결되는지 확인하세요.")
