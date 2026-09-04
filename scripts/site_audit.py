#!/usr/bin/env python3
"""
사이트 구조 점검: 제목·메타·H1·H2(질문형 비율)·CTA 존재·이미지 alt 누락.
  python3 scripts/site_audit.py                       # sitemap에서 페이지 수집
  python3 scripts/site_audit.py https://morningwalkbooks.com/consulting-2/ ...   # 특정 URL
출력: content/reports/site-audit-YYYY-MM-DD.md
의존: pip3 install requests beautifulsoup4
"""
import sys, os, re, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.environ.get("SITE_URL", "")
CTA_WORDS = []

def main():
    global SITE
    if not SITE:
        import re as _re
        try:
            SITE = _re.search(r"사이트 주소.*?(https?://\S+)", open(os.path.join(ROOT,"skills","common","site.md"),encoding="utf-8").read()).group(1).rstrip("/")
        except Exception:
            print("site.md에 사이트 주소가 없습니다. /setup 먼저."); sys.exit(1)
    import requests
    from bs4 import BeautifulSoup
    urls = sys.argv[1:]
    if not urls:
        for sm in (f"{SITE}/sitemap.xml", f"{SITE}/wp-sitemap.xml", f"{SITE}/sitemap_index.xml"):
            try:
                t = requests.get(sm, timeout=15).text
                locs = re.findall(r"<loc>(.*?)</loc>", t)
                subs = [l for l in locs if l.endswith(".xml")]
                for s in subs:
                    locs += re.findall(r"<loc>(.*?)</loc>", requests.get(s, timeout=15).text)
                urls = [l for l in locs if not l.endswith(".xml")]
                if urls: break
            except Exception: continue
    if not urls: print("URL 없음. sitemap을 못 찾았으면 URL을 직접 넘길 것."); sys.exit(1)
    rows = []
    for u in urls[:200]:
        try:
            html = requests.get(u, timeout=20, headers={"User-Agent": "mw-audit"}).text
        except Exception as e:
            rows.append((u, "FETCH FAIL", "", "", "", "", "", "")); continue
        s = BeautifulSoup(html, "html.parser")
        title = (s.title.string or "").strip() if s.title else ""
        meta = s.find("meta", attrs={"name": "description"}); meta = (meta.get("content") or "").strip() if meta else ""
        h1 = len(s.find_all("h1")); h2s = [h.get_text(" ", strip=True) for h in s.find_all(["h2", "h3"])]
        q = sum(1 for h in h2s if re.search(r"\?|까요|인가요|하나요|무엇|어떻게|얼마", h))
        text = s.get_text(" ", strip=True)
        cta = any(w in text for w in CTA_WORDS)
        imgs = s.find_all("img"); noalt = sum(1 for i in imgs if not (i.get("alt") or "").strip())
        rows.append((u, title[:60], len(meta), h1, len(h2s), f"{q}/{len(h2s)}", "Y" if cta else "N", f"{noalt}/{len(imgs)}"))
    os.makedirs(os.path.join(ROOT, "content", "reports"), exist_ok=True)
    out = os.path.join(ROOT, "content", "reports", f"site-audit-{datetime.date.today().isoformat()}.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"# 사이트 점검 {datetime.date.today()}\n\n| URL | 제목 | 메타길이 | H1수 | H2/H3수 | 질문형 | CTA | alt누락 |\n|---|---|---|---|---|---|---|---|\n")
        for r in rows: f.write("| " + " | ".join(str(x) for x in r) + " |\n")
        f.write("\n## 점검 기준\n- 메타 150자 내외, H1 1개, H2/H3 질문형 비율 높을수록 AI Overview 구조에 부합, CTA 없는 페이지는 전환 누수, alt 누락은 접근성·이미지 검색.\n")
    print(f"저장: {out} ({len(rows)}페이지)")

if __name__ == "__main__":
    main()
