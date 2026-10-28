#!/usr/bin/env python3
"""
Doenjang vs Miso (ID 3575) 글을 워드프레스 리비전으로 복원한다.
  python scripts/wp_restore_3575.py             # 리비전 목록 표시
  python scripts/wp_restore_3575.py --restore N  # 리비전 N번으로 복원
"""
import json, re, sys, os, argparse
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(ROOT, "secrets", "wp.json")
c = json.load(open(CFG, encoding="utf-8"))
c["url"] = c["url"].rstrip("/")

import requests
auth = (c["user"], c["app_password"])
api = c["url"] + "/wp-json/wp/v2"

POST_ID = 3575

ap = argparse.ArgumentParser()
ap.add_argument("--restore", type=int, help="복원할 리비전 ID")
args = ap.parse_args()

# 리비전 목록 가져오기
r = requests.get(api + f"/posts/{POST_ID}/revisions", params={
    "_fields": "id,date,content",
    "per_page": 30,
}, auth=auth, timeout=20)

if not r.ok:
    print(f"리비전 읽기 실패: {r.status_code} {r.text[:200]}")
    sys.exit(1)

revisions = r.json()

# 업로드한 파일명들 (이게 포함된 리비전은 수정된 것)
our_files = [
    "KakaoTalk_20261028_184832477_01",
    "KakaoTalk_20261028_184832477_04",
    "KakaoTalk_20261028_185036697_03",
    "KakaoTalk_20261028_185036697_04",
    "KakaoTalk_20261028_184836160",
]

if not args.restore:
    print(f"글 #{POST_ID} 리비전 목록 (최신순):\n")
    for rev in revisions:
        content = rev["content"]["rendered"]
        has_our = any(f in content for f in our_files)
        marker = " ← 우리 이미지 포함" if has_our else " ★ 원본"
        length = len(content)
        print(f"  ID: {rev['id']}  |  {rev['date']}  |  {length}글자{marker}")

    # 원본 리비전 찾기 (우리 이미지가 없는 가장 최근 것)
    original = None
    for rev in revisions:
        content = rev["content"]["rendered"]
        if not any(f in content for f in our_files):
            original = rev
            break

    if original:
        print(f"\n복원 추천: ID {original['id']} ({original['date']})")
        print(f"실행: python scripts/wp_restore_3575.py --restore {original['id']}")
    else:
        print("\n⚠ 원본 리비전을 찾지 못했습니다.")
else:
    # 리비전 복원
    rev_id = args.restore
    print(f"리비전 {rev_id}로 복원 중...")

    # 해당 리비전의 content 가져오기
    target = None
    for rev in revisions:
        if rev["id"] == rev_id:
            target = rev
            break

    if not target:
        # 직접 가져오기
        r2 = requests.get(api + f"/posts/{POST_ID}/revisions/{rev_id}", params={
            "_fields": "id,content",
            "context": "edit"
        }, auth=auth, timeout=20)
        if r2.ok:
            target = r2.json()
        else:
            print(f"리비전 {rev_id}를 찾을 수 없습니다: {r2.status_code}")
            sys.exit(1)

    # raw content 가져오기 (edit context)
    r3 = requests.get(api + f"/posts/{POST_ID}/revisions/{rev_id}", params={
        "_fields": "content",
        "context": "edit"
    }, auth=auth, timeout=20)
    if not r3.ok:
        print(f"리비전 raw content 가져오기 실패: {r3.status_code}")
        sys.exit(1)

    raw_content = r3.json()["content"]["raw"]

    r4 = requests.post(
        api + f"/posts/{POST_ID}",
        auth=auth,
        json={"content": raw_content},
        timeout=30,
    )
    if r4.ok:
        print(f"복원 완료!")
        print(f"확인: {c['url']}/wp-admin/post.php?post={POST_ID}&action=edit")
    else:
        print(f"복원 실패: {r4.status_code} {r4.text[:300]}")
