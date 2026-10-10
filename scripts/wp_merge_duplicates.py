#!/usr/bin/env python3
"""
중복 글 자동 정리: 내용 비교 → 합치기 → 휴지통 → 301 리다이렉트 (Rank Math)

사용법:
  python scripts/wp_merge_duplicates.py --test          # 연결 확인
  python scripts/wp_merge_duplicates.py --dry-run       # 실제 변경 없이 미리보기
  python scripts/wp_merge_duplicates.py                 # 실행

의존: pip install requests beautifulsoup4
secrets/wp.json 필요 (wp_post.py와 동일)
"""
import sys, os, json, re, argparse, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(ROOT, "secrets", "wp.json")

PAIRS = [
    {
        "name": "1. 백김치",
        "keep_slug": "white-kimchi-recipe-clean-flavor-without-chili",
        "remove_slug": "baek-kimchi-recipe-white-kimchi-without-chili",
    },
    {
        "name": "2. 김치 종류",
        "keep_slug": "kimchi-varieties-by-region-200-types-explained",
        "remove_slug": "kimchi-varieties-by-region-200-types-explained-2",
    },
    {
        "name": "3. 깍두기",
        "keep_slug": "kkakdugi-golden-recipe-the-secret-to-that-perfect-crunch",
        "remove_slug": "kkakdugi-recipe-the-secret-to-perfect-crunch",
    },
    {
        "name": "4. 간장 가이드",
        "keep_slug": "the-complete-guide-to-korean-soy-sauce-types",
        "remove_slug": "korean-soy-sauce-a-complete-guide-by-type",
    },
    {
        "name": "5. 발효 식품 보관법",
        "keep_slug": "how-to-store-fermented-foods-the-right-way",
        "remove_slug": "how-to-store-korean-fermented-foods-properly",
    },
    {
        "name": "6. 김치찌개",
        "keep_slug": "kimchi-jjigae-the-perfect-fermented-stew-recipe",
        "remove_slug": "kimchi-jjigae-the-perfect-fermented-stew-recipe-2",
    },
]


def load():
    if not os.path.exists(CFG):
        print("secrets/wp.json 없음. wp_post.py --test 먼저 실행하세요.")
        sys.exit(2)
    c = json.load(open(CFG, encoding="utf-8"))
    c["url"] = c["url"].rstrip("/")
    return c


def get_post_by_slug(api, auth, slug):
    r = requests.get(
        api + "/posts",
        params={"slug": slug, "status": "publish,draft,private", "_fields": "id,title,content,slug,link,status"},
        auth=auth,
        timeout=20,
    )
    if not r.ok:
        print(f"  검색 실패 ({slug}): {r.status_code}")
        return None
    posts = r.json()
    return posts[0] if posts else None


def strip_html(html):
    from bs4 import BeautifulSoup
    return BeautifulSoup(html, "html.parser").get_text(separator="\n", strip=True)


def find_unique_sections(keep_html, remove_html):
    from bs4 import BeautifulSoup

    keep_soup = BeautifulSoup(keep_html, "html.parser")
    remove_soup = BeautifulSoup(remove_html, "html.parser")

    keep_text = keep_soup.get_text(separator=" ", strip=True).lower()

    unique_blocks = []
    for el in remove_soup.find_all(["p", "h2", "h3", "h4", "ul", "ol", "table", "blockquote"]):
        el_text = el.get_text(separator=" ", strip=True)
        if len(el_text) < 20:
            continue
        check = el_text[:80].lower()
        if check not in keep_text:
            unique_blocks.append(str(el))

    return unique_blocks


def add_rankmath_redirect(api, auth, source_url, target_url, dry_run=False):
    redirect_api = api.replace("/wp/v2", "/rankmath/v1")
    payload = {
        "sources": [{"pattern": source_url, "comparison": "exact"}],
        "url_to": target_url,
        "header_code": 301,
        "status": "active",
    }
    if dry_run:
        print(f"  [미리보기] 301 리다이렉트: {source_url} → {target_url}")
        return True

    r = requests.post(
        redirect_api + "/redirections",
        auth=auth,
        json=payload,
        timeout=20,
    )
    if r.ok:
        print(f"  301 리다이렉트 설정 완료: {source_url} → {target_url}")
        return True

    # Rank Math REST API가 없으면 수동 안내
    if r.status_code == 404:
        print(f"  Rank Math REST API 없음 — 수동으로 리다이렉트 설정 필요:")
        print(f"    원본: {source_url}")
        print(f"    대상: {target_url}")
        return False
    print(f"  리다이렉트 실패: {r.status_code} {r.text[:200]}")
    return False


def process_pair(pair, api, auth, base_url, dry_run=False):
    print(f"\n{'='*60}")
    print(f"[{pair['name']}]")
    print(f"  남길 글: {pair['keep_slug']}")
    print(f"  삭제할 글: {pair['remove_slug']}")

    keep = get_post_by_slug(api, auth, pair["keep_slug"])
    remove = get_post_by_slug(api, auth, pair["remove_slug"])

    if not keep and not remove:
        print("  두 글 모두 없음 — 건너뜀")
        return "skip"

    if not keep:
        print(f"  남길 글 없음 — 삭제할 글({pair['remove_slug']})의 슬러그를 변경해야 합니다")
        if remove and not dry_run:
            new_slug = pair["keep_slug"]
            r = requests.post(
                api + f"/posts/{remove['id']}",
                auth=auth,
                json={"slug": new_slug},
                timeout=20,
            )
            if r.ok:
                print(f"  슬러그 변경 완료: {pair['remove_slug']} → {new_slug}")
                return "renamed"
            print(f"  슬러그 변경 실패: {r.status_code}")
        return "skip"

    if not remove:
        print("  삭제할 글 이미 없음 — 건너뜀")
        return "skip"

    keep_content = keep["content"].get("rendered", "")
    remove_content = remove["content"].get("rendered", "")
    keep_title = keep["title"].get("rendered", "")
    remove_title = remove["title"].get("rendered", "")

    print(f"  남길 글: [{keep['id']}] {keep_title} ({keep['status']})")
    print(f"  삭제할 글: [{remove['id']}] {remove_title} ({remove['status']})")

    keep_len = len(strip_html(keep_content))
    remove_len = len(strip_html(remove_content))
    print(f"  글자 수 — 남김: {keep_len}자, 삭제: {remove_len}자")

    # 삭제할 글에서 남길 글에 없는 내용 추출
    unique = find_unique_sections(keep_content, remove_content)
    if unique:
        print(f"  삭제할 글에서 고유 단락 {len(unique)}개 발견 → 남길 글 끝에 추가")
        merged = keep_content.rstrip()
        merged += "\n\n<!-- 중복 글에서 합침 -->\n"
        merged += "\n".join(unique)

        if not dry_run:
            r = requests.post(
                api + f"/posts/{keep['id']}",
                auth=auth,
                json={"content": merged},
                timeout=20,
            )
            if r.ok:
                print(f"  내용 합치기 완료")
            else:
                print(f"  합치기 실패: {r.status_code} {r.text[:200]}")
                return "error"
        else:
            print(f"  [미리보기] 내용 합치기 예정")
    else:
        print(f"  삭제할 글에 고유 내용 없음 — 합칠 것 없음")

    # 삭제할 글 → 휴지통
    if not dry_run:
        r = requests.delete(
            api + f"/posts/{remove['id']}",
            auth=auth,
            timeout=20,
        )
        if r.ok:
            print(f"  휴지통 이동 완료: [{remove['id']}] {remove_title}")
        else:
            print(f"  휴지통 실패: {r.status_code} {r.text[:200]}")
            return "error"
    else:
        print(f"  [미리보기] 휴지통 이동 예정: [{remove['id']}]")

    # 301 리다이렉트
    source = f"/{pair['remove_slug']}/"
    target = f"{base_url}/{pair['keep_slug']}/"
    add_rankmath_redirect(api, auth, source, target, dry_run)

    return "done"


import requests

def main():
    ap = argparse.ArgumentParser(description="중복 글 자동 정리")
    ap.add_argument("--test", action="store_true", help="연결 확인만")
    ap.add_argument("--dry-run", action="store_true", help="실제 변경 없이 미리보기")
    a = ap.parse_args()

    c = load()
    auth = (c["user"], c["app_password"])
    api = c["url"] + "/wp-json/wp/v2"
    base_url = c["url"]

    if a.test:
        r = requests.get(api + "/users/me", auth=auth, timeout=20)
        if r.ok:
            print("연결 성공:", r.json().get("name"))
        else:
            print("연결 실패:", r.status_code, r.text[:200])
        return

    mode = "미리보기" if a.dry_run else "실행"
    print(f"중복 글 정리 [{mode}]")
    print(f"대상: {base_url}")
    print(f"처리할 쌍: {len(PAIRS)}개")

    if not a.dry_run:
        print("\n주의: 실제로 글을 수정하고 휴지통으로 보냅니다.")
        print("먼저 --dry-run 으로 확인하세요.")
        ans = input("계속하시겠습니까? (y/n): ").strip().lower()
        if ans != "y":
            print("취소됨")
            return

    results = {"done": 0, "skip": 0, "error": 0, "renamed": 0}
    for pair in PAIRS:
        result = process_pair(pair, api, auth, base_url, a.dry_run)
        results[result] = results.get(result, 0) + 1
        time.sleep(1)

    print(f"\n{'='*60}")
    print(f"완료: {results['done']}건 처리, {results['skip']}건 건너뜀, "
          f"{results.get('renamed', 0)}건 슬러그 변경, {results['error']}건 오류")

    if not a.dry_run:
        print("\n다음 할 것:")
        print("1. wp-admin에서 합쳐진 글 확인 (내용이 자연스러운지)")
        print("2. Rank Math 리다이렉트가 안 됐으면 수동 설정")
        print("3. GSC → URL 검사 → 삭제된 URL과 남긴 URL 모두 인덱싱 요청")


if __name__ == "__main__":
    main()
