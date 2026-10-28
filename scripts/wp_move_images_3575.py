#!/usr/bin/env python3
"""
Doenjang vs Miso (ID 3575) 글에서
이미지/동영상 블록을 올바른 섹션 위치로 이동한다.
raw content (블록 에디터 포맷) 사용.
"""
import json, re, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(ROOT, "secrets", "wp.json")
c = json.load(open(CFG, encoding="utf-8"))
c["url"] = c["url"].rstrip("/")

import requests
auth = (c["user"], c["app_password"])
api = c["url"] + "/wp-json/wp/v2"

# 1. raw content 가져오기
r = requests.get(api + "/posts/3575", params={
    "_fields": "content",
    "context": "edit"
}, auth=auth, timeout=20)
if not r.ok:
    print(f"글 읽기 실패: {r.status_code}")
    sys.exit(1)

content = r.json()["content"]["raw"]
print(f"글 길이: {len(content)} 글자")

# 2. 미디어 ID별로 블록 찾기
media_ids = [3997, 3999, 4000, 4001, 4002]
blocks = {}

for mid in media_ids:
    # wp:image 블록
    pat = re.compile(
        rf'<!-- wp:image \{{[^}}]*"id":{mid}[^}}]*\}} -->\s*<figure[^>]*>.*?</figure>\s*<!-- /wp:image -->',
        re.DOTALL
    )
    m = pat.search(content)
    if m:
        blocks[mid] = m.group(0)
        print(f"  블록 찾음: ID {mid} (image)")
        continue

    # wp:video 블록
    pat = re.compile(
        rf'<!-- wp:video \{{[^}}]*"id":{mid}[^}}]*\}} -->\s*<figure[^>]*>.*?</figure>\s*<!-- /wp:video -->',
        re.DOTALL
    )
    m = pat.search(content)
    if m:
        blocks[mid] = m.group(0)
        print(f"  블록 찾음: ID {mid} (video)")
        continue

    # figure 태그에 wp-image-ID 포함
    pat = re.compile(
        rf'<figure[^>]*>.*?wp-image-{mid}.*?</figure>',
        re.DOTALL
    )
    m = pat.search(content)
    if m:
        blocks[mid] = m.group(0)
        print(f"  블록 찾음: ID {mid} (figure)")
        continue

    print(f"  ⚠ ID {mid} 블록을 찾지 못함")

# 동영상 - URL로 찾기 (ID 패턴 못 찾았을 때)
if 3997 not in blocks:
    vid_url = "KakaoTalk_20261028_184836160.mp4"
    pat = re.compile(
        r'<!-- wp:(?:video|image)[^-]*-->\s*<figure[^>]*>.*?' + re.escape(vid_url) + r'.*?</figure>\s*<!-- /wp:(?:video|image) -->',
        re.DOTALL
    )
    m = pat.search(content)
    if m:
        blocks[3997] = m.group(0)
        print(f"  블록 찾음: ID 3997 (URL 매칭)")
    else:
        pat2 = re.compile(r'<figure[^>]*>.*?' + re.escape(vid_url) + r'.*?</figure>', re.DOTALL)
        m2 = pat2.search(content)
        if m2:
            blocks[3997] = m2.group(0)
            print(f"  블록 찾음: ID 3997 (figure URL)")

if not blocks:
    print("\n미디어 블록을 하나도 찾지 못했습니다.")
    sys.exit(1)

print(f"\n총 {len(blocks)}개 블록 발견")

# 3. 기존 블록들을 본문에서 제거
cleaned = content
for mid, block_html in blocks.items():
    cleaned = cleaned.replace(block_html, "")

cleaned = re.sub(r'\n{4,}', '\n\n\n', cleaned)

# 4. h2 헤딩 위치 찾기
heading_positions = []
for m in re.finditer(r'<!-- wp:heading[^-]*-->.*?<!-- /wp:heading -->', cleaned, re.DOTALL):
    text = re.sub(r'<[^>]+>', '', m.group(0)).strip()
    heading_positions.append((m.start(), text, m.group(0)))

# heading이 wp:heading 블록이 아닌 경우 일반 h2 태그로 찾기
if not heading_positions:
    for m in re.finditer(r'<h2[^>]*>(.*?)</h2>', cleaned, re.DOTALL):
        text = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        heading_positions.append((m.start(), text, m.group(0)))

print("\n섹션 목록:")
for pos, text, _ in heading_positions:
    print(f"  위치 {pos}: {text}")

# 5. 배치 계획 (뒤에서부터 삽입해야 위치가 안 밀림)
plan = [
    ("Why the flavors land differently", [4002]),
    ("One mass, or two phases", [3999, 3997]),
    ("What actually grows on meju", [4001]),
    ("Same biochemistry, different machinery", [4000]),
]

for heading_text, mid_list in plan:
    target_pos = None
    for pos, text, full_tag in heading_positions:
        if heading_text.lower() in text.lower():
            target_pos = pos
            break

    if target_pos is None:
        print(f"\n⚠ '{heading_text}' 헤딩을 찾지 못함")
        continue

    insert_html = "\n\n"
    inserted = []
    for mid in mid_list:
        if mid in blocks:
            insert_html += blocks[mid] + "\n\n"
            inserted.append(mid)

    if inserted:
        cleaned = cleaned[:target_pos] + insert_html + cleaned[target_pos:]
        print(f"\n'{heading_text}' 앞에 {inserted} 삽입 (위치 {target_pos})")

# 6. 업데이트
r = requests.post(
    api + "/posts/3575",
    auth=auth,
    json={"content": cleaned},
    timeout=30,
)
if r.ok:
    print(f"\n완료! 이미지/동영상이 각 섹션에 배치되었습니다.")
    print(f"확인: {c['url']}/wp-admin/post.php?post=3575&action=edit")
else:
    print(f"\n업데이트 실패: {r.status_code} {r.text[:300]}")
