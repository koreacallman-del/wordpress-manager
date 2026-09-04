#!/usr/bin/env python3
"""
워드프레스 REST API로 글을 초안(draft)으로 올린다.
  python scripts/wp_post.py content/articles/2026-09-05-slug.md --draft
  python scripts/wp_post.py content/tools/slug.html --draft
  python scripts/wp_post.py --test        # 연결 확인
secrets/wp.json: {"url":"https://example.com","user":"아이디","app_password":"xxxx xxxx xxxx"}
의존: pip install requests markdown
"""
import sys, os, json, re, argparse
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(ROOT, "secrets", "wp.json")

def load():
    if not os.path.exists(CFG):
        print("secrets/wp.json 이 없습니다. /setup 에서 워드프레스 연결을 먼저 하세요."); sys.exit(2)
    c = json.load(open(CFG, encoding="utf-8")); c["url"] = c["url"].rstrip("/"); return c

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("file", nargs="?"); ap.add_argument("--draft", action="store_true"); ap.add_argument("--test", action="store_true"); a = ap.parse_args()
    import requests
    c = load(); auth = (c["user"], c["app_password"]); api = c["url"] + "/wp-json/wp/v2"
    if a.test:
        r = requests.get(api + "/users/me", auth=auth, timeout=20)
        print("연결 성공:", r.json().get("name")) if r.ok else print("연결 실패:", r.status_code, r.text[:200]); return
    if not a.file: print(__doc__); sys.exit(1)
    text = open(a.file, encoding="utf-8").read()
    if a.file.endswith(".html"):
        title = re.search(r"<title>(.*?)</title>", text, re.S); title = title.group(1).strip() if title else os.path.basename(a.file)
        body = re.search(r"<body[^>]*>(.*)</body>", text, re.S); content = body.group(1) if body else text
        # 스타일·스크립트는 그대로 포함 (사용자 정의 HTML 블록과 동일 효과)
        style = re.search(r"<style>(.*?)</style>", text, re.S); content = (f"<style>{style.group(1)}</style>" if style else "") + content
        excerpt = ""
    else:
        import markdown
        meta = re.search(r"메타.*?[:：]\s*(.+)", text); excerpt = meta.group(1).strip() if meta else ""
        if re.match(r"^[^\n#]", text):
            parts = re.split(r"^---\s*$", text, maxsplit=1, flags=re.M)
            text = parts[1] if len(parts) > 1 else text
        m = re.search(r"^#\s*(.+)", text, re.M); title = m.group(1).strip() if m else os.path.basename(a.file)
        text = re.sub(r"^#\s*.+\n", "", text, count=1, flags=re.M)
        content = markdown.markdown(text, extensions=["tables", "fenced_code"])
    r = requests.post(api + "/posts", auth=auth, json={"title": title, "content": content, "status": "draft", "excerpt": excerpt}, timeout=30)
    if r.ok:
        j = r.json(); print(f"초안 업로드 완료: {j.get('link')}  (편집: {c['url']}/wp-admin/post.php?post={j.get('id')}&action=edit)")
    else:
        print("업로드 실패:", r.status_code, r.text[:300])

if __name__ == "__main__":
    main()
