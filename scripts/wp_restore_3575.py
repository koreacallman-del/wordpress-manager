#!/usr/bin/env python3
"""
Doenjang vs Miso (ID 3575) 글에서
업로드했던 이미지/동영상을 전부 제거하여 원래 글로 복원한다.
"""
import json, re, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(ROOT, "secrets", "wp.json")
c = json.load(open(CFG, encoding="utf-8"))
c["url"] = c["url"].rstrip("/")

import requests
auth = (c["user"], c["app_password"])
api = c["url"] + "/wp-json/wp/v2"

POST_ID = 3575

# 제거할 미디어 ID와 파일명
REMOVE = {
    3997: "KakaoTalk_20261028_184836160.mp4",
    3999: "KakaoTalk_20261028_184832477_01.jpg",
    4000: "KakaoTalk_20261028_184832477_04.jpg",
    4001: "KakaoTalk_20261028_185036697_03.jpg",
    4002: "KakaoTalk_20261028_185036697_04.jpg",
}

# raw content 가져오기
r = requests.get(api + f"/posts/{POST_ID}", params={
    "_fields": "content",
    "context": "edit"
}, auth=auth, timeout=20)
if not r.ok:
    print(f"글 읽기 실패: {r.status_code}")
    sys.exit(1)

content = r.json()["content"]["raw"]
print(f"현재 길이: {len(content)} 글자")

cleaned = content
total_removed = 0

for mid, filename in REMOVE.items():
    # wp:image 블록
    for pat in [
        re.compile(rf'<!-- wp:image \{{[^}}]*"id":{mid}[^}}]*\}} -->\s*<figure[^>]*>.*?</figure>\s*<!-- /wp:image -->\s*', re.DOTALL),
        re.compile(rf'<!-- wp:video \{{[^}}]*"id":{mid}[^}}]*\}} -->\s*<figure[^>]*>.*?</figure>\s*<!-- /wp:video -->\s*', re.DOTALL),
        re.compile(rf'<figure[^>]*>\s*<img[^>]*wp-image-{mid}[^>]*/?>.*?</figure>\s*', re.DOTALL),
        re.compile(rf'<figure[^>]*>.*?{re.escape(filename)}.*?</figure>\s*', re.DOTALL),
        re.compile(rf'<img[^>]*{re.escape(filename)}[^>]*/?\>\s*', re.DOTALL),
    ]:
        found = pat.findall(cleaned)
        if found:
            total_removed += len(found)
            print(f"  제거: ID {mid} ({filename}) x{len(found)}")
        cleaned = pat.sub('', cleaned)

cleaned = re.sub(r'\n{4,}', '\n\n', cleaned)

print(f"\n총 {total_removed}개 미디어 블록 제거")
print(f"복원 후 길이: {len(cleaned)} 글자")

# 업데이트
r = requests.post(
    api + f"/posts/{POST_ID}",
    auth=auth,
    json={"content": cleaned},
    timeout=30,
)
if r.ok:
    print(f"\n원래 글로 복원 완료!")
    print(f"확인: {c['url']}/wp-admin/post.php?post={POST_ID}&action=edit")
else:
    print(f"\n복원 실패: {r.status_code} {r.text[:300]}")
