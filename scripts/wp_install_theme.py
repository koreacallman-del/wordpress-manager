#!/usr/bin/env python3
"""
Fermentpedia 차일드 테마 ZIP 생성 + 설치 안내

사용법:
  python scripts/wp_install_theme.py          # ZIP 생성
  python scripts/wp_install_theme.py --check  # 현재 활성 테마 확인

의존: pip install requests
"""
import sys, os, json, argparse, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THEME_DIR = os.path.join(ROOT, "themes", "fermentpedia-child")
ZIP_PATH = os.path.join(ROOT, "fermentpedia-child.zip")
CFG = os.path.join(ROOT, "secrets", "wp.json")


def load():
    if not os.path.exists(CFG):
        print("secrets/wp.json 없음"); sys.exit(2)
    c = json.load(open(CFG, encoding="utf-8"))
    c["url"] = c["url"].rstrip("/")
    return c


def build_zip():
    if os.path.exists(ZIP_PATH):
        os.remove(ZIP_PATH)

    with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zf:
        for dirpath, _, filenames in os.walk(THEME_DIR):
            for f in filenames:
                full = os.path.join(dirpath, f)
                arcname = os.path.join(
                    "fermentpedia-child",
                    os.path.relpath(full, THEME_DIR)
                )
                zf.write(full, arcname)

    size = os.path.getsize(ZIP_PATH) / 1024
    print(f"ZIP 생성 완료: {ZIP_PATH} ({size:.1f} KB)")
    return ZIP_PATH


def check_theme(c):
    import requests
    auth = (c["user"], c["app_password"])
    r = requests.get(
        c["url"] + "/wp-json/wp/v2/themes",
        auth=auth,
        timeout=20,
    )
    if not r.ok:
        print(f"테마 조회 실패: {r.status_code}")
        return

    active = None
    child_installed = False

    for t in r.json():
        if t.get("status") == "active":
            active = t
        if t.get("stylesheet") == "fermentpedia-child":
            child_installed = True

    if active:
        name = active.get("name", {})
        if isinstance(name, dict):
            name = name.get("raw", "?")
        print(f"활성 테마: {name}")
        print(f"스타일시트: {active.get('stylesheet', '?')}")

    if child_installed:
        print("fermentpedia-child: 설치됨")
    else:
        print("fermentpedia-child: 미설치")


def try_activate(c):
    import requests
    auth = (c["user"], c["app_password"])
    r = requests.post(
        c["url"] + "/wp-json/wp/v2/themes/fermentpedia-child",
        auth=auth,
        json={"status": "active"},
        timeout=20,
    )
    if r.ok:
        print("테마 활성화 완료!")
        return True
    print(f"활성화 실패 ({r.status_code}) — wp-admin에서 수동 활성화 필요")
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="현재 테마 상태 확인")
    ap.add_argument("--activate", action="store_true", help="이미 설치된 테마 활성화")
    a = ap.parse_args()

    c = load()

    if a.check:
        check_theme(c)
        return

    if a.activate:
        try_activate(c)
        return

    # ZIP 생성
    build_zip()

    print()
    print("=" * 50)
    print("설치 방법:")
    print("=" * 50)
    print()
    print("1. WordPress 관리자 로그인")
    print("   → 외모(Appearance) → 테마(Themes)")
    print()
    print("2. '새로 추가(Add New)' → '테마 업로드(Upload Theme)'")
    print()
    print(f"3. 파일 선택: fermentpedia-child.zip")
    print("   → '지금 설치(Install Now)' 클릭")
    print()
    print("4. '활성화(Activate)' 클릭")
    print()
    print("5. 활성화 후 확인:")
    print("   python scripts/wp_install_theme.py --check")
    print()
    print("또는 설치만 하고 여기서 활성화:")
    print("   python scripts/wp_install_theme.py --activate")


if __name__ == "__main__":
    main()
