#!/usr/bin/env python3
"""
Doenjang vs Miso (ID 3575) 글에서
중복 이미지/동영상을 전부 제거한 뒤, 각 섹션 앞에 한 번만 삽입한다.
"""
import json, re, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(ROOT, "secrets", "wp.json")
c = json.load(open(CFG, encoding="utf-8"))
c["url"] = c["url"].rstrip("/")

import requests
auth = (c["user"], c["app_password"])
api = c["url"] + "/wp-json/wp/v2"

POST_ID = 3575

# 업로드된 미디어 정보
MEDIA = {
    3999: {
        "type": "image",
        "url": "https://fermentpedia.com/wp-content/uploads/2026/10/KakaoTalk_20261028_184832477_01.jpg",
        "alt": "Mixing homemade doenjang by hand before transferring to onggi",
    },
    4000: {
        "type": "image",
        "url": "https://fermentpedia.com/wp-content/uploads/2026/10/KakaoTalk_20261028_184832477_04.jpg",
        "alt": "Doenjang base and soaked barley ready for mixing",
    },
    4001: {
        "type": "image",
        "url": "https://fermentpedia.com/wp-content/uploads/2026/10/KakaoTalk_20261028_185036697_03.jpg",
        "alt": "Adding ground barley rice to the doenjang base",
    },
    4002: {
        "type": "image",
        "url": "https://fermentpedia.com/wp-content/uploads/2026/10/KakaoTalk_20261028_185036697_04.jpg",
        "alt": "Doenjang packed into a traditional Korean onggi pot",
    },
    3997: {
        "type": "video",
        "url": "https://fermentpedia.com/wp-content/uploads/2026/10/KakaoTalk_20261028_184836160.mp4",
        "alt": "Mixing doenjang by hand",
    },
}

# 배치 계획: (섹션 제목, [미디어 ID 리스트])
PLAN = [
    ("Same biochemistry, different machinery", [4000]),
    ("What actually grows on meju", [4001]),
    ("One mass, or two phases", [3999, 3997]),
    ("Why the flavors land differently", [4002]),
]

# 1. raw content 가져오기
r = requests.get(api + f"/posts/{POST_ID}", params={
    "_fields": "content",
    "context": "edit"
}, auth=auth, timeout=20)
if not r.ok:
    print(f"글 읽기 실패: {r.status_code}")
    sys.exit(1)

content = r.json()["content"]["raw"]
print(f"원본 길이: {len(content)} 글자")

# 2. 업로드된 미디어와 관련된 모든 것을 제거
cleaned = content

for mid, info in MEDIA.items():
    # 파일명 추출
    filename = info["url"].split("/")[-1]
    filename_noext = filename.rsplit(".", 1)[0]

    # 패턴 1: <!-- wp:image {"id":XXXX} --> ... <!-- /wp:image -->
    pat = re.compile(
        rf'<!-- wp:image \{{[^}}]*"id":{mid}[^}}]*\}} -->\s*<figure[^>]*>.*?</figure>\s*<!-- /wp:image -->\s*',
        re.DOTALL
    )
    count = len(pat.findall(cleaned))
    if count:
        print(f"  제거: wp:image ID {mid} x{count}")
    cleaned = pat.sub('', cleaned)

    # 패턴 2: <!-- wp:video {"id":XXXX} --> ... <!-- /wp:video -->
    pat = re.compile(
        rf'<!-- wp:video \{{[^}}]*"id":{mid}[^}}]*\}} -->\s*<figure[^>]*>.*?</figure>\s*<!-- /wp:video -->\s*',
        re.DOTALL
    )
    count = len(pat.findall(cleaned))
    if count:
        print(f"  제거: wp:video ID {mid} x{count}")
    cleaned = pat.sub('', cleaned)

    # 패턴 3: figure 태그에 wp-image-ID
    pat = re.compile(
        rf'<figure[^>]*class="[^"]*wp-block-image[^"]*"[^>]*>\s*<img[^>]*wp-image-{mid}[^>]*/>\s*(?:<figcaption[^>]*>.*?</figcaption>\s*)?</figure>\s*',
        re.DOTALL
    )
    count = len(pat.findall(cleaned))
    if count:
        print(f"  제거: figure wp-image-{mid} x{count}")
    cleaned = pat.sub('', cleaned)

    # 패턴 4: figure에 파일 URL 포함 (video/image)
    pat = re.compile(
        rf'<figure[^>]*>.*?{re.escape(filename)}.*?</figure>\s*',
        re.DOTALL
    )
    count = len(pat.findall(cleaned))
    if count:
        print(f"  제거: figure with {filename} x{count}")
    cleaned = pat.sub('', cleaned)

    # 패턴 5: 단독 img 태그
    pat = re.compile(
        rf'<img[^>]*{re.escape(filename)}[^>]*/?\>\s*',
        re.DOTALL
    )
    count = len(pat.findall(cleaned))
    if count:
        print(f"  제거: img tag {filename} x{count}")
    cleaned = pat.sub('', cleaned)

    # 패턴 6: <!-- wp:image --> 없이 figure만 있는 경우 (wp-image-ID)
    pat = re.compile(
        rf'<figure[^>]*>\s*<img[^>]*wp-image-{mid}[^>]*/?>.*?</figure>\s*',
        re.DOTALL
    )
    count = len(pat.findall(cleaned))
    if count:
        print(f"  제거: loose figure wp-image-{mid} x{count}")
    cleaned = pat.sub('', cleaned)

# 빈 줄 정리
cleaned = re.sub(r'\n{4,}', '\n\n', cleaned)

print(f"\n정리 후 길이: {len(cleaned)} 글자")

# 3. 새 블록 HTML 생성
def make_image_block(mid, info):
    return (
        f'<!-- wp:image {{"id":{mid},"sizeSlug":"large","linkDestination":"none"}} -->\n'
        f'<figure class="wp-block-image size-large">'
        f'<img src="{info["url"]}" alt="{info["alt"]}" class="wp-image-{mid}"/>'
        f'<figcaption class="wp-element-caption">{info["alt"]}</figcaption>'
        f'</figure>\n'
        f'<!-- /wp:image -->'
    )

def make_video_block(mid, info):
    return (
        f'<!-- wp:video {{"id":{mid}}} -->\n'
        f'<figure class="wp-block-video">'
        f'<video controls src="{info["url"]}"></video>'
        f'<figcaption class="wp-element-caption">{info["alt"]}</figcaption>'
        f'</figure>\n'
        f'<!-- /wp:video -->'
    )

# 4. 섹션 위치 찾기 (뒤에서부터 삽입)
for heading_text, mid_list in reversed(PLAN):
    # wp:heading 블록 안의 h2
    pat = re.compile(
        rf'(<!-- wp:heading[^-]*-->\s*<h2[^>]*>.*?{re.escape(heading_text)}.*?</h2>\s*<!-- /wp:heading -->)',
        re.DOTALL | re.IGNORECASE
    )
    m = pat.search(cleaned)

    # wp:heading 블록이 아닌 일반 h2
    if not m:
        pat = re.compile(
            rf'(<h2[^>]*>.*?{re.escape(heading_text)}.*?</h2>)',
            re.DOTALL | re.IGNORECASE
        )
        m = pat.search(cleaned)

    if not m:
        print(f"⚠ '{heading_text}' 섹션을 찾지 못함")
        continue

    insert_html = "\n\n"
    inserted = []
    for mid in mid_list:
        info = MEDIA[mid]
        if info["type"] == "image":
            insert_html += make_image_block(mid, info) + "\n\n"
        else:
            insert_html += make_video_block(mid, info) + "\n\n"
        inserted.append(mid)

    pos = m.start()
    cleaned = cleaned[:pos] + insert_html + cleaned[pos:]
    print(f"'{heading_text}' 앞에 {inserted} 삽입")

# 5. 업데이트
r = requests.post(
    api + f"/posts/{POST_ID}",
    auth=auth,
    json={"content": cleaned},
    timeout=30,
)
if r.ok:
    print(f"\n완료!")
    print(f"확인: {c['url']}/wp-admin/post.php?post={POST_ID}&action=edit")
else:
    print(f"\n업데이트 실패: {r.status_code} {r.text[:300]}")
