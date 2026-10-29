#!/usr/bin/env python3
"""
Child theme 파일을 워드프레스 테마 편집기 API로 업데이트한다.
WP REST API에는 테마 파일 편집 엔드포인트가 없으므로
wp-admin 로그인 세션을 사용한다.

실행: python scripts/wp_update_theme.py
"""
import json, os, re, sys
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(ROOT, "secrets", "wp.json")
c = json.load(open(CFG, encoding="utf-8"))
c["url"] = c["url"].rstrip("/")

THEME_DIR = os.path.join(ROOT, "themes", "fermentpedia-child")
THEME_SLUG = "fermentpedia-child"

FILES_TO_UPDATE = ["functions.php", "style.css"]

session = requests.Session()

# --- 1. wp-login.php 로 로그인 ---
print("워드프레스 로그인 중...")
login_url = c["url"] + "/wp-login.php"
r = session.get(login_url, timeout=20)
if not r.ok:
    print(f"로그인 페이지 접근 실패: {r.status_code}")
    sys.exit(1)

login_data = {
    "log": c["user"],
    "pwd": c["app_password"].replace(" ", ""),
    "wp-submit": "Log In",
    "redirect_to": c["url"] + "/wp-admin/",
    "testcookie": "1",
}

# app_password는 공백 포함 형태일 수 있음 — 일반 비밀번호로도 시도
r = session.post(login_url, data=login_data, allow_redirects=True, timeout=20)

# 로그인 성공 확인
if "wp-admin" not in r.url and "dashboard" not in r.text.lower():
    # app_password 원본으로 재시도
    login_data["pwd"] = c["app_password"]
    r = session.post(login_url, data=login_data, allow_redirects=True, timeout=20)

if "wp-admin" not in r.url and "dashboard" not in r.text.lower():
    print("로그인 실패. secrets/wp.json의 비밀번호를 확인하세요.")
    print("(앱 비밀번호는 wp-admin 로그인에 사용할 수 없습니다.)")
    print("")
    print("대안: 아래 명령어로 REST API를 통해 업데이트하세요.")
    print("  방법 1: wp-admin → 외모 → 테마 파일 편집기에서 수동 붙여넣기")
    print("  방법 2: Hostinger hPanel → 파일 관리자 → wp-content/themes/fermentpedia-child/")
    sys.exit(1)

print("  로그인 성공!")

# --- 2. 테마 편집 페이지에서 nonce 얻기 ---
print("테마 편집기 nonce 가져오는 중...")
editor_url = c["url"] + f"/wp-admin/theme-editor.php?theme={THEME_SLUG}"
r = session.get(editor_url, timeout=20)
if not r.ok:
    print(f"테마 편집기 접근 실패: {r.status_code}")
    sys.exit(1)

nonce_match = re.search(r'name="_wpnonce"\s+value="([^"]+)"', r.text)
if not nonce_match:
    nonce_match = re.search(r'"_wpnonce":"([^"]+)"', r.text)
if not nonce_match:
    nonce_match = re.search(r'_wpnonce=([a-f0-9]+)', r.text)

if not nonce_match:
    print("nonce를 찾을 수 없습니다. 테마 편집기가 비활성화되었을 수 있습니다.")
    sys.exit(1)

nonce = nonce_match.group(1)
print(f"  nonce: {nonce[:8]}...")

# --- 3. 각 파일 업데이트 ---
for filename in FILES_TO_UPDATE:
    filepath = os.path.join(THEME_DIR, filename)
    if not os.path.exists(filepath):
        print(f"  !! 파일 없음: {filepath}")
        continue

    content = open(filepath, encoding="utf-8").read()
    print(f"\n{filename} 업데이트 중 ({len(content)} bytes)...")

    # wp-admin/theme-editor.php POST
    post_data = {
        "_wpnonce": nonce,
        "_wp_http_referer": f"/wp-admin/theme-editor.php?file={filename}&theme={THEME_SLUG}",
        "newcontent": content,
        "action": "update",
        "file": filename,
        "theme": THEME_SLUG,
        "submit": "Update File",
    }

    r = session.post(
        c["url"] + "/wp-admin/theme-editor.php",
        data=post_data,
        allow_redirects=True,
        timeout=30,
    )

    if r.ok and ("updated successfully" in r.text.lower() or "파일을 수정했습니다" in r.text or r.status_code == 200):
        # 성공 여부 더 정확히 확인
        if "error" in r.text.lower() and "fatal" in r.text.lower():
            print(f"  !! PHP 오류 감지 — 파일이 저장되지 않았을 수 있습니다")
            print(f"  사이트 확인 필요: {c['url']}")
        else:
            print(f"  OK: {filename} 업데이트 완료!")
    else:
        print(f"  !! 업데이트 실패: {r.status_code}")
        # 에러 내용 추출 시도
        err = re.search(r'<div[^>]*class="[^"]*error[^"]*"[^>]*>(.*?)</div>', r.text, re.S)
        if err:
            print(f"  에러: {err.group(1).strip()[:200]}")

print(f"\n완료! 사이트 확인: {c['url']}")
print("문제가 있으면 wp-admin → 외모 → 테마 편집기에서 확인하세요.")
