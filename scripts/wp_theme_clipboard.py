#!/usr/bin/env python3
"""
Child theme 파일을 클립보드에 복사하고 WP 테마 편집기를 연다.
각 파일마다: 클립보드 복사 → 브라우저 열기 → 사용자가 Ctrl+A, Ctrl+V, 저장

실행: python scripts/wp_theme_clipboard.py
"""
import json, os, sys, subprocess, webbrowser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(ROOT, "secrets", "wp.json")
c = json.load(open(CFG, encoding="utf-8"))
c["url"] = c["url"].rstrip("/")

THEME_DIR = os.path.join(ROOT, "themes", "fermentpedia-child")
THEME_SLUG = "fermentpedia-child"

files = [
    ("style.css", "스타일"),
    ("functions.php", "기능"),
]

def copy_to_clipboard(text):
    proc = subprocess.Popen(["clip"], stdin=subprocess.PIPE)
    proc.communicate(text.encode("utf-8"))

for filename, label in files:
    filepath = os.path.join(THEME_DIR, filename)
    if not os.path.exists(filepath):
        print(f"!! 파일 없음: {filepath}")
        continue

    content = open(filepath, encoding="utf-8").read()
    copy_to_clipboard(content)

    editor_url = (
        f"{c['url']}/wp-admin/theme-editor.php"
        f"?file={filename}&theme={THEME_SLUG}"
    )

    print(f"\n{'='*50}")
    print(f"  {filename} ({label}) — 클립보드에 복사됨! ({len(content)} bytes)")
    print(f"{'='*50}")
    print(f"  브라우저가 열립니다.")
    print(f"  1. 편집기의 코드 전체 선택: Ctrl+A")
    print(f"  2. 붙여넣기: Ctrl+V")
    print(f"  3. 아래 '파일 업데이트' 버튼 클릭")
    print()

    webbrowser.open(editor_url)

    if filename != files[-1][0]:
        input("  완료되면 Enter를 눌러 다음 파일로 →  ")

print(f"\n완료! 사이트 확인: {c['url']}")
print("PageSpeed Insights에서 다시 측정해보세요.")
