#!/usr/bin/env python3
"""
Doenjang vs Miso (ID 3575) 글에서
이미지/동영상 블록을 올바른 섹션 위치로 이동한다.
"""
import json, re, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(ROOT, "secrets", "wp.json")
c = json.load(open(CFG, encoding="utf-8"))
c["url"] = c["url"].rstrip("/")

import requests
auth = (c["user"], c["app_password"])
api = c["url"] + "/wp-json/wp/v2"

# 1. 글 가져오기
r = requests.get(api + "/posts/3575", params={"_fields": "content"}, auth=auth, timeout=20)
if not r.ok:
    print(f"글 읽기 실패: {r.status_code}"); sys.exit(1)

content = r.json()["content"]["rendered"]

# 2. 업로드된 이미지/동영상 블록 추출 (wp:image, wp:video 블록)
media_ids = {3999, 4000, 4001, 4002, 3997}

# wp:image 블록 패턴
img_pattern = re.compile(
    r'<!-- wp:image \{[^}]*"id":(\d+)[^}]*\} -->\s*<figure[^>]*>.*?</figure>\s*<!-- /wp:image -->',
    re.DOTALL
)
# wp:video 블록 패턴
vid_pattern = re.compile(
    r'<!-- wp:video \{[^}]*"id":(\d+)[^}]*\} -->\s*<figure[^>]*>.*?</figure>\s*<!-- /wp:video -->',
    re.DOTALL
)
# 간단한 video/image 태그 (블록 아닌 경우)
simple_vid = re.compile(
    r'<figure[^>]*class="wp-block-video[^"]*"[^>]*>.*?</figure>',
    re.DOTALL
)
simple_img = re.compile(
    r'<figure[^>]*class="wp-block-image[^"]*"[^>]*>.*?wp-image-(\d+).*?</figure>',
    re.DOTALL
)

blocks = {}

# wp:image 블록 찾기
for m in img_pattern.finditer(content):
    mid = int(m.group(1))
    if mid in media_ids:
        blocks[mid] = m.group(0)

# wp:video 블록 찾기
for m in vid_pattern.finditer(content):
    mid = int(m.group(1))
    if mid in media_ids:
        blocks[mid] = m.group(0)

# 블록 형태가 아닌 경우 figure 태그로 찾기
for m in simple_img.finditer(content):
    mid = int(m.group(1))
    if mid in media_ids and mid not in blocks:
        blocks[mid] = m.group(0)

# 동영상 URL로 찾기
vid_url = "KakaoTalk_20261028_184836160.mp4"
vid_tag_pattern = re.compile(
    r'<figure[^>]*>.*?' + re.escape(vid_url) + r'.*?</figure>',
    re.DOTALL
)
for m in vid_tag_pattern.finditer(content):
    if 3997 not in blocks:
        blocks[3997] = m.group(0)

# 못 찾은 블록 - 간단한 img 태그로 시도
for mid in media_ids:
    if mid not in blocks:
        pat = re.compile(
            rf'<figure[^>]*>.*?wp-image-{mid}.*?</figure>',
            re.DOTALL
        )
        m = pat.search(content)
        if m:
            blocks[mid] = m.group(0)

# 동영상 - comment 형태 없이 삽입된 경우
if 3997 not in blocks:
    pat = re.compile(r'<!-- wp:image[^-]*-->\s*<figure[^>]*>.*?' + re.escape(vid_url) + r'.*?</figure>\s*<!-- /wp:image -->', re.DOTALL)
    m = pat.search(content)
    if m:
        blocks[3997] = m.group(0)

print(f"찾은 미디어 블록: {list(blocks.keys())}")

if not blocks:
    print("미디어 블록을 찾지 못했습니다.")
    sys.exit(1)

# 3. 기존 블록들을 본문에서 제거
cleaned = content
for mid, block_html in blocks.items():
    cleaned = cleaned.replace(block_html, "")

# 빈 줄 정리
cleaned = re.sub(r'\n{4,}', '\n\n\n', cleaned)

# 4. 각 섹션 앞에 이미지 삽입
# 배치 계획:
#   "Same biochemistry" 앞 → ID 4000 (준비 - 두 그릇)
#   "What actually grows on meju" 앞 → ID 4001 (보리쌀 넣기)
#   "One mass, or two phases" 앞 → ID 3999 (손으로 비비기) + 동영상 3997
#   "Why the flavors land differently" 앞 → ID 4002 (항아리)

placements = [
    ("Same biochemistry, different machinery", [4000]),
    ("What actually grows on meju", [4001]),
    ("One mass, or two phases", [3999, 3997]),
    ("Why the flavors land differently", [4002]),
]

for heading_text, mid_list in placements:
    insert_html = "\n\n"
    for mid in mid_list:
        if mid in blocks:
            insert_html += blocks[mid] + "\n\n"

    if insert_html.strip():
        # h2 태그 찾기
        h2_pattern = re.compile(
            rf'(<h2[^>]*>.*?{re.escape(heading_text)}.*?</h2>)',
            re.DOTALL | re.IGNORECASE
        )
        m = h2_pattern.search(cleaned)
        if m:
            cleaned = cleaned[:m.start()] + insert_html + cleaned[m.start():]
            print(f"  '{heading_text}' 앞에 {mid_list} 삽입")
        else:
            print(f"  ⚠ '{heading_text}' 섹션을 찾지 못함")

# 5. 업데이트
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
    print(f"업데이트 실패: {r.status_code} {r.text[:300]}")
