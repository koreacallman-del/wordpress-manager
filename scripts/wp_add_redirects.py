#!/usr/bin/env python3
"""
301 리다이렉트 설정 — Rank Math REST API 또는 mu-plugin 방식

사용법:
  python scripts/wp_add_redirects.py              # Rank Math API 시도
  python scripts/wp_add_redirects.py --mu-plugin   # mu-plugin PHP 파일 생성

의존: pip install requests
"""
import sys, os, json, argparse
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(ROOT, "secrets", "wp.json")

REDIRECTS = [
    ("/kkakdugi-recipe-the-secret-to-perfect-crunch/",
     "/kkakdugi-golden-recipe-the-secret-to-that-perfect-crunch/"),
    ("/korean-soy-sauce-a-complete-guide-by-type/",
     "/the-complete-guide-to-korean-soy-sauce-types/"),
    ("/how-to-store-korean-fermented-foods-properly/",
     "/how-to-store-fermented-foods-the-right-way/"),
]

MU_PLUGIN_PHP = """<?php
/**
 * Plugin Name: Fermentpedia 301 Redirects
 * Description: 중복 글 301 리다이렉트. 설정 후 삭제 가능.
 */
if (!defined('ABSPATH')) exit;

add_action('template_redirect', function() {
    $redirects = [
        '/kkakdugi-recipe-the-secret-to-perfect-crunch/' => '/kkakdugi-golden-recipe-the-secret-to-that-perfect-crunch/',
        '/korean-soy-sauce-a-complete-guide-by-type/' => '/the-complete-guide-to-korean-soy-sauce-types/',
        '/how-to-store-korean-fermented-foods-properly/' => '/how-to-store-fermented-foods-the-right-way/',
    ];
    $path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
    $path = rtrim($path, '/') . '/';
    if (isset($redirects[$path])) {
        wp_redirect(home_url($redirects[$path]), 301);
        exit;
    }
});
"""


def load():
    if not os.path.exists(CFG):
        print("secrets/wp.json 없음"); sys.exit(2)
    c = json.load(open(CFG, encoding="utf-8"))
    c["url"] = c["url"].rstrip("/")
    return c


def try_rankmath_api(c):
    import requests
    auth = (c["user"], c["app_password"])
    base = c["url"] + "/wp-json"

    endpoints = [
        "/rankmath/v1/redirections",
        "/rankmath/v1/updateRedirection",
    ]

    for source, target in REDIRECTS:
        success = False
        for ep in endpoints:
            payload = {
                "sources": [{"pattern": source, "comparison": "exact"}],
                "url_to": target,
                "header_code": 301,
                "status": "active",
            }
            r = requests.post(base + ep, auth=auth, json=payload, timeout=20)
            if r.ok:
                print(f"  성공: {source} → {target}")
                success = True
                break

        if not success:
            return False
    return True


def generate_mu_plugin():
    out = os.path.join(ROOT, "fermentpedia-redirects.php")
    with open(out, "w", encoding="utf-8") as f:
        f.write(MU_PLUGIN_PHP)
    print(f"mu-plugin 파일 생성: {out}")
    return out


def try_upload_mu_plugin(c, filepath):
    """wp-json으로 플러그인 업로드 시도 (WP 5.5+)"""
    import requests
    auth = (c["user"], c["app_password"])
    api = c["url"] + "/wp-json/wp/v2"

    with open(filepath, "rb") as f:
        r = requests.post(
            api + "/plugins",
            auth=auth,
            files={"file": ("fermentpedia-redirects.php", f, "application/php")},
            timeout=30,
        )

    if r.ok:
        print("  플러그인 업로드 성공!")
        plugin_slug = r.json().get("plugin", "")
        # 활성화
        r2 = requests.post(
            api + f"/plugins",
            auth=auth,
            json={"plugin": plugin_slug, "status": "active"},
            timeout=20,
        )
        if r2.ok:
            print("  플러그인 활성화 완료!")
            return True
        # 활성화 endpoint가 다를 수 있음
        r3 = requests.put(
            api + f"/plugins/{plugin_slug}",
            auth=auth,
            json={"status": "active"},
            timeout=20,
        )
        if r3.ok:
            print("  플러그인 활성화 완료!")
            return True
        print(f"  업로드됨, 수동 활성화 필요: wp-admin → 플러그인")
        return True

    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mu-plugin", action="store_true", help="PHP 파일만 생성")
    a = ap.parse_args()

    c = load()

    if a.mu_plugin:
        filepath = generate_mu_plugin()
        print(f"\n이 파일을 워드프레스에 업로드하세요:")
        print(f"  위치: wp-content/mu-plugins/fermentpedia-redirects.php")
        print(f"  방법: 호스팅 파일 매니저 또는 FTP")
        return

    print("301 리다이렉트 설정 시작")
    print(f"대상: {c['url']}")
    print(f"리다이렉트: {len(REDIRECTS)}건\n")

    # 1차: Rank Math REST API
    print("[1단계] Rank Math REST API 시도...")
    import requests
    if try_rankmath_api(c):
        print("\nRank Math API로 설정 완료!")
        return

    print("  Rank Math REST API 사용 불가\n")

    # 2차: mu-plugin 생성 + 업로드 시도
    print("[2단계] mu-plugin 생성 + WordPress API 업로드 시도...")
    filepath = generate_mu_plugin()
    if try_upload_mu_plugin(c, filepath):
        print("\n리다이렉트 설정 완료!")
        print("확인: 브라우저에서 아래 URL 접속 시 자동 이동되는지 확인")
        for s, t in REDIRECTS:
            print(f"  {c['url']}{s}")
        return

    print("  WordPress 플러그인 API 업로드 불가\n")

    # 3차: 수동 안내
    print("[3단계] 수동 업로드 필요")
    print(f"  생성된 파일: {filepath}")
    print()
    print("방법 A — 호스팅 파일 매니저:")
    print("  1. 호스팅 cPanel/관리자 → 파일 매니저")
    print("  2. wp-content/mu-plugins/ 폴더로 이동 (없으면 생성)")
    print(f"  3. {os.path.basename(filepath)} 업로드")
    print()
    print("방법 B — wp-admin에서 직접:")
    print("  1. wp-admin → 플러그인 → 새로 추가 → 플러그인 업로드")
    print(f"  2. {os.path.basename(filepath)} 선택 → 설치 → 활성화")
    print()
    print("업로드 후 확인:")
    for s, t in REDIRECTS:
        print(f"  {c['url']}{s} → {t}")


if __name__ == "__main__":
    main()
