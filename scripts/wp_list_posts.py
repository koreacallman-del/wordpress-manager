#!/usr/bin/env python3
"""발행된 글 목록 출력"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(ROOT, "secrets", "wp.json")
c = json.load(open(CFG, encoding="utf-8"))
c["url"] = c["url"].rstrip("/")

import requests
auth = (c["user"], c["app_password"])
api = c["url"] + "/wp-json/wp/v2"

page = 1
while True:
    r = requests.get(api + "/posts", params={
        "per_page": 50, "page": page,
        "status": "publish",
        "_fields": "id,title,slug"
    }, auth=auth, timeout=20)
    if not r.ok:
        break
    posts = r.json()
    if not posts:
        break
    for p in posts:
        title = p["title"]["rendered"]
        print(f"{p['id']} | {title} | {p['slug']}")
    page += 1
