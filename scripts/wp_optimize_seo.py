#!/usr/bin/env python3
"""
상위 노출 글 제목·메타 디스크립션 최적화 + Best Probiotic Foods 콘텐츠 교체

사용법:
  python scripts/wp_optimize_seo.py --dry-run    # 미리보기
  python scripts/wp_optimize_seo.py              # 실행

의존: pip install requests markdown
"""
import sys, os, json, re, argparse, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(ROOT, "secrets", "wp.json")

# (post_id, seo_title, meta_description, focus_keyword)
SEO_UPDATES = [
    (2908,
     "Mukeunji: What Happens When Kimchi Ages for a Year",
     "Mukeunji is kimchi fermented for months or years. Here's how aging changes its flavor, texture, and bacterial profile — plus three ways to cook with it.",
     "mukeunji"),
    (2683,
     "What Happens When You Eat Doenjang Soup Every Day?",
     "Doenjang jjigae is a Korean staple made from fermented soybean paste. Here's what daily consumption does to your gut bacteria, blood pressure, and nutrient intake.",
     "doenjang soup"),
    (2672,
     "Ganjang Gejang: Why Koreans Eat Raw Crab in Soy Sauce",
     "Ganjang gejang is raw crab marinated in soy sauce — Korea's most prized seafood dish. The fermentation science that makes it safe and intensely flavorful.",
     "ganjang gejang"),
    (2680,
     "What Is Nuruk? Korea's Wild Fermentation Starter Explained",
     "Nuruk is the traditional Korean fermentation starter used to make makgeolli, soju, and fermented pastes. Here's how it works and why it matters.",
     "nuruk"),
    (2848,
     "How to Store Fermented Foods (Without Killing the Bacteria)",
     "Wrong storage kills live cultures in kimchi, sauerkraut, and other fermented foods. The temperature, container, and timing rules that keep them alive.",
     "how to store fermented foods"),
    (2650,
     "How Vinegar Is Made: The 2-Stage Fermentation Process",
     "Vinegar starts as alcohol and ends as acetic acid. The two-stage fermentation process — and how Korean traditional vinegar differs from commercial versions.",
     "vinegar fermentation"),
    (2851,
     "White Kimchi Recipe: Non-Spicy, Probiotic, Ready in 3 Days",
     "Baek-kimchi is a mild, non-spicy Korean kimchi made without chili. This recipe uses traditional fermentation — ready to eat in 3 days.",
     "white kimchi recipe"),
    (2911,
     "Maesil-cheong: Korea's Green Plum Syrup (Is It Fermented?)",
     "Maesil-cheong is a Korean green plum syrup often called an enzyme. Here's what actually happens during the sugar-extraction process — and why it's not true fermentation.",
     "maesil cheong"),
    (2664,
     "Cheonggukjang vs Natto: Same Bacteria, Different Taste",
     "Both cheonggukjang and natto ferment with Bacillus subtilis, but they taste nothing alike. The key differences in process, flavor, and nutrition.",
     "cheonggukjang vs natto"),
    (2678,
     "What Is Jeotgal? Korean Fermented Seafood Explained",
     "Jeotgal is Korean fermented seafood — salted shrimp, anchovies, and fish aged for months. How it's made, why it's essential to kimchi, and how to use it.",
     "jeotgal"),
    (2681,
     "Does Kimchi Help You Lose Weight? Here's What Studies Found",
     "Some studies link kimchi to weight loss through gut bacteria changes. We reviewed the research — here's what holds up and what doesn't.",
     "kimchi weight loss"),
    (3575,
     "Doenjang vs Miso: What's the Real Difference?",
     "Doenjang and miso are both fermented soybean pastes, but they're made differently. How fermentation, flavor, and nutrition compare side by side.",
     "doenjang vs miso"),
    (2647,
     "How Gochujang Is Made: The Fermentation Behind the Heat",
     "Gochujang is a Korean chili paste fermented with meju, glutinous rice, and gochugaru. The science behind its complex sweet-spicy-umami flavor.",
     "gochujang fermentation"),
    (2644,
     "The Science of Kimchi Fermentation: How LAB Build Flavor",
     "Lactic acid bacteria transform salted cabbage into kimchi through a predictable microbial succession. Here's what happens at each stage of fermentation.",
     "kimchi fermentation science"),
    (2643,
     "What Is Fermentation? Types, Science, and Why It Matters",
     "Fermentation is a metabolic process where microorganisms convert sugars into acids, gases, or alcohol. The science behind every fermented food you eat.",
     "what is fermentation"),
]


def load():
    if not os.path.exists(CFG):
        print("secrets/wp.json 없음"); sys.exit(2)
    c = json.load(open(CFG, encoding="utf-8"))
    c["url"] = c["url"].rstrip("/")
    return c


def update_seo_meta(api, auth, post_id, seo_title, description, keyword, dry_run):
    import requests
    if dry_run:
        print(f"  [미리보기] SEO 제목: {seo_title}")
        print(f"  [미리보기] 메타: {description[:80]}...")
        return True

    r = requests.post(
        api + f"/posts/{post_id}",
        auth=auth,
        json={
            "meta": {
                "rank_math_title": seo_title,
                "rank_math_description": description,
                "rank_math_focus_keyword": keyword,
            }
        },
        timeout=20,
    )
    if r.ok:
        print(f"  SEO 메타 업데이트 완료")
        return True
    print(f"  실패: {r.status_code} {r.text[:200]}")
    return False


def update_probiotic_foods(api, auth, dry_run):
    import requests, markdown

    article_path = os.path.join(ROOT, "content", "articles", "2026-09-04-best-probiotic-foods.md")
    if not os.path.exists(article_path):
        print("  기사 파일 없음: " + article_path)
        return False

    text = open(article_path, encoding="utf-8").read()

    meta = re.search(r"메타.*?[:：]\s*(.+)", text)
    excerpt = meta.group(1).strip() if meta else ""

    if re.match(r"^[^\n#]", text):
        parts = re.split(r"^---\s*$", text, maxsplit=1, flags=re.M)
        text = parts[1] if len(parts) > 1 else text

    m = re.search(r"^#\s*(.+)", text, re.M)
    title = m.group(1).strip() if m else "Best Probiotic Foods"
    text = re.sub(r"^#\s*.+\n", "", text, count=1, flags=re.M)
    content = markdown.markdown(text, extensions=["tables", "fenced_code"])

    post_id = 3342

    if dry_run:
        print(f"  [미리보기] 글 #{post_id} 콘텐츠 교체 예정")
        print(f"  [미리보기] 제목: {title}")
        print(f"  [미리보기] 본문: {len(content)}자")
        return True

    r = requests.post(
        api + f"/posts/{post_id}",
        auth=auth,
        json={
            "title": title,
            "content": content,
            "excerpt": excerpt,
        },
        timeout=30,
    )
    if r.ok:
        print(f"  콘텐츠 교체 완료: #{post_id}")
        return True
    print(f"  실패: {r.status_code} {r.text[:200]}")
    return False


def delete_old_draft(api, auth, dry_run):
    """이전 초안 #3337 삭제"""
    import requests
    r = requests.get(api + "/posts/3337", auth=auth, params={"status": "draft,publish,private"}, timeout=20)
    if not r.ok:
        print("  #3337 없음 — 건너뜀")
        return
    if dry_run:
        print(f"  [미리보기] 초안 #3337 휴지통 이동 예정")
        return
    r = requests.delete(api + f"/posts/3337", auth=auth, timeout=20)
    if r.ok:
        print(f"  초안 #3337 휴지통 이동 완료")
    else:
        print(f"  #3337 삭제 실패: {r.status_code}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    import requests
    c = load()
    auth = (c["user"], c["app_password"])
    api = c["url"] + "/wp-json/wp/v2"
    mode = "미리보기" if a.dry_run else "실행"

    print(f"SEO 최적화 + Best Probiotic Foods 교체 [{mode}]")
    print(f"대상: {c['url']}\n")

    if not a.dry_run:
        ans = input("계속하시겠습니까? (y/n): ").strip().lower()
        if ans != "y":
            print("취소됨"); return

    # 1. SEO 제목·메타 업데이트
    print("=" * 60)
    print("[1단계] SEO 제목·메타 디스크립션 최적화")
    print(f"대상: {len(SEO_UPDATES)}개 글\n")

    success = 0
    for post_id, title, desc, kw in SEO_UPDATES:
        print(f"[#{post_id}] {title}")
        if update_seo_meta(api, auth, post_id, title, desc, kw, a.dry_run):
            success += 1
        time.sleep(0.5)

    print(f"\nSEO 업데이트: {success}/{len(SEO_UPDATES)}건 완료")

    # 2. Best Probiotic Foods 콘텐츠 교체
    print("\n" + "=" * 60)
    print("[2단계] Best Probiotic Foods 콘텐츠 교체 (#3342)")
    update_probiotic_foods(api, auth, a.dry_run)

    # 2b. SEO 메타도 업데이트
    print("\n[2b] Best Probiotic Foods SEO 메타 설정")
    update_seo_meta(api, auth, 3342,
        "Best Probiotic Foods: What Actually Has Live Cultures",
        "A science-based guide to the best probiotic foods, with CFU comparisons, Korean fermented foods, and how to tell if a product still has live cultures.",
        "best probiotic foods",
        a.dry_run)

    # 3. 이전 초안 삭제
    print("\n" + "=" * 60)
    print("[3단계] 이전 초안 #3337 정리")
    delete_old_draft(api, auth, a.dry_run)

    print("\n" + "=" * 60)
    print("완료!")
    if not a.dry_run:
        print("\n확인 사항:")
        print("1. 각 글 편집 → Rank Math 탭에서 SEO 제목·메타 확인")
        print("2. Best Probiotic Foods 글 내용 확인")
        print("3. GSC → URL 검사 → 변경된 글 인덱싱 요청")


if __name__ == "__main__":
    main()
