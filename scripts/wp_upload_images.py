#!/usr/bin/env python3
"""
기존 워드프레스 글에 이미지를 업로드하고 삽입한다.

사용법:
  # 1단계: 된장 관련 글 찾기
  python scripts/wp_upload_images.py --search doenjang

  # 2단계: 이미지 업로드 + 글에 삽입
  python scripts/wp_upload_images.py --post-id 1234 --images img1.jpg img2.jpg img3.jpg

  # 캡션(alt text) 지정
  python scripts/wp_upload_images.py --post-id 1234 --images img1.jpg img2.jpg --captions "Mixing doenjang" "Doenjang in onggi"

  # 글 맨 앞에 삽입 (기본은 맨 뒤)
  python scripts/wp_upload_images.py --post-id 1234 --images img1.jpg --position top

  # 이미지만 미디어 라이브러리에 올리기 (글에 삽입 안 함)
  python scripts/wp_upload_images.py --images img1.jpg img2.jpg

secrets/wp.json 필요: {"url":"https://...","user":"...","app_password":"xxxx"}
"""
import sys, os, json, argparse, mimetypes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(ROOT, "secrets", "wp.json")

def load_config():
    if not os.path.exists(CFG):
        print("secrets/wp.json 이 없습니다.")
        sys.exit(2)
    c = json.load(open(CFG, encoding="utf-8"))
    c["url"] = c["url"].rstrip("/")
    return c

def search_posts(cfg, keyword):
    import requests
    auth = (cfg["user"], cfg["app_password"])
    api = cfg["url"] + "/wp-json/wp/v2"
    r = requests.get(api + "/posts", params={
        "search": keyword,
        "per_page": 20,
        "status": "publish,draft",
        "_fields": "id,title,slug,status,link"
    }, auth=auth, timeout=20)
    if not r.ok:
        print(f"검색 실패: {r.status_code}")
        return
    posts = r.json()
    if not posts:
        print(f"'{keyword}' 관련 글을 찾지 못했습니다.")
        return
    print(f"\n'{keyword}' 검색 결과 ({len(posts)}개):\n")
    for p in posts:
        title = p["title"]["rendered"]
        status = "발행" if p["status"] == "publish" else "초안"
        print(f"  ID: {p['id']}  |  [{status}] {title}")
        print(f"       {p['link']}\n")

def upload_image(cfg, filepath):
    import requests
    auth = (cfg["user"], cfg["app_password"])
    api = cfg["url"] + "/wp-json/wp/v2"

    filename = os.path.basename(filepath)
    mime, _ = mimetypes.guess_type(filepath)
    if not mime:
        mime = "image/jpeg"

    with open(filepath, "rb") as f:
        data = f.read()

    r = requests.post(
        api + "/media",
        auth=auth,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": mime,
        },
        data=data,
        timeout=120,
    )
    if r.ok:
        j = r.json()
        print(f"  업로드 완료: {filename} → ID {j['id']}")
        print(f"  URL: {j['source_url']}")
        return j
    else:
        print(f"  업로드 실패 ({filename}): {r.status_code} {r.text[:200]}")
        return None

def insert_images_to_post(cfg, post_id, media_list, captions, position):
    import requests
    auth = (cfg["user"], cfg["app_password"])
    api = cfg["url"] + "/wp-json/wp/v2"

    r = requests.get(api + f"/posts/{post_id}", params={
        "_fields": "id,title,content"
    }, auth=auth, timeout=20)
    if not r.ok:
        print(f"글 {post_id} 읽기 실패: {r.status_code}")
        return
    post = r.json()
    content = post["content"]["rendered"]
    title = post["title"]["rendered"]

    image_html = "\n\n"
    for i, media in enumerate(media_list):
        url = media["source_url"]
        mid = media["id"]
        alt = captions[i] if i < len(captions) else ""
        image_html += f'<!-- wp:image {{"id":{mid},"sizeSlug":"large"}} -->\n'
        image_html += f'<figure class="wp-block-image size-large">'
        image_html += f'<img src="{url}" alt="{alt}" class="wp-image-{mid}"/>'
        if alt:
            image_html += f'<figcaption class="wp-element-caption">{alt}</figcaption>'
        image_html += f'</figure>\n'
        image_html += f'<!-- /wp:image -->\n\n'

    if position == "top":
        new_content = image_html + content
    else:
        new_content = content + image_html

    r = requests.post(
        api + f"/posts/{post_id}",
        auth=auth,
        json={"content": new_content},
        timeout=30,
    )
    if r.ok:
        print(f"\n  '{title}' 에 이미지 {len(media_list)}개 삽입 완료!")
        print(f"  확인: {cfg['url']}/wp-admin/post.php?post={post_id}&action=edit")
    else:
        print(f"  글 업데이트 실패: {r.status_code} {r.text[:200]}")

def upload_video(cfg, filepath):
    import requests
    auth = (cfg["user"], cfg["app_password"])
    api = cfg["url"] + "/wp-json/wp/v2"

    filename = os.path.basename(filepath)
    mime, _ = mimetypes.guess_type(filepath)
    if not mime:
        mime = "video/mp4"

    filesize = os.path.getsize(filepath)
    print(f"  동영상 업로드 중: {filename} ({filesize / 1024 / 1024:.1f} MB)...")

    with open(filepath, "rb") as f:
        data = f.read()

    r = requests.post(
        api + "/media",
        auth=auth,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": mime,
        },
        data=data,
        timeout=600,
    )
    if r.ok:
        j = r.json()
        print(f"  업로드 완료: {filename} → ID {j['id']}")
        print(f"  URL: {j['source_url']}")
        return j
    else:
        print(f"  업로드 실패 ({filename}): {r.status_code} {r.text[:200]}")
        return None

def main():
    ap = argparse.ArgumentParser(description="워드프레스 이미지/동영상 업로드")
    ap.add_argument("--search", help="키워드로 글 검색")
    ap.add_argument("--post-id", type=int, help="이미지를 삽입할 글 ID")
    ap.add_argument("--images", nargs="+", help="업로드할 이미지 파일 경로들")
    ap.add_argument("--video", help="업로드할 동영상 파일 경로")
    ap.add_argument("--captions", nargs="*", default=[], help="각 이미지의 캡션 (alt text)")
    ap.add_argument("--position", choices=["top", "bottom"], default="bottom",
                     help="이미지 삽입 위치 (기본: bottom)")
    args = ap.parse_args()

    cfg = load_config()

    if args.search:
        search_posts(cfg, args.search)
        return

    if not args.images and not args.video:
        print("--images 또는 --video 를 지정하세요. --search 로 글을 먼저 검색할 수 있습니다.")
        ap.print_help()
        return

    media_list = []

    if args.images:
        print(f"\n이미지 {len(args.images)}개 업로드 중...\n")
        for img_path in args.images:
            if not os.path.exists(img_path):
                print(f"  파일 없음: {img_path}")
                continue
            result = upload_image(cfg, img_path)
            if result:
                media_list.append(result)

    if args.video:
        if not os.path.exists(args.video):
            print(f"  파일 없음: {args.video}")
        else:
            result = upload_video(cfg, args.video)
            if result:
                media_list.append(result)

    if media_list and args.post_id:
        print(f"\n글 ID {args.post_id}에 삽입 중...")
        insert_images_to_post(cfg, args.post_id, media_list, args.captions, args.position)
    elif media_list:
        print(f"\n미디어 라이브러리에 {len(media_list)}개 업로드 완료.")
        print("글에 삽입하려면 --post-id 옵션을 추가하세요.")

if __name__ == "__main__":
    main()
