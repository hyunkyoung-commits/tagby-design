#!/usr/bin/env python3
"""
tagby-article.html의 카드 썸네일(aspect-[4/3])을 추출해
500×375 PNG로 캡처 → design-study-article/thum/ 에 저장
"""
import os, re, glob
from playwright.sync_api import sync_playwright

BASE        = "/Volumes/KIOXIA/작업폴더/클로드코드 워크폴더/대행사업부 웹사이트"
TAGBY_PATH  = os.path.join(BASE, "tagby-article.html")
ARTICLE_DIR = os.path.join(BASE, "design-study-article")
THUM_DIR    = os.path.join(ARTICLE_DIR, "thum")
os.makedirs(THUM_DIR, exist_ok=True)

PRETENDARD_LINK = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">'
TAILWIND_SCRIPT = '<script src="https://cdn.tailwindcss.com"></script>'

W, H = 500, 375   # 4:3 logical; DPR=2 → 1000×750 physical output
DPR  = 2


def find_div_end(content, start):
    pos, depth = start, 0
    while pos < len(content):
        no = content.find('<div', pos)
        nc = content.find('</div>', pos)
        if nc == -1:
            break
        if no == -1:
            no = len(content)
        if no < nc:
            depth += 1
            pos = no + 4
        else:
            depth -= 1
            pos = nc + 6
            if depth == 0:
                return pos
    return -1


def extract_card_thumbnails(tagby):
    """tagby-article.html에서 {slug: thumb_html} 반환"""
    result = {}
    pos = 0
    while True:
        href_idx = tagby.find('href="design-study-article/', pos)
        if href_idx == -1:
            break
        slug_start = href_idx + len('href="design-study-article/')
        slug_end = tagby.find('.html"', slug_start)
        if slug_end == -1:
            pos = href_idx + 1
            continue
        slug = tagby[slug_start:slug_end]

        next_href_idx = tagby.find('<a href="design-study-article/', href_idx + 1)
        scope_end = next_href_idx if next_href_idx != -1 else href_idx + 5000

        thumb_start = tagby.find('<div class="aspect-[4/3]', href_idx, scope_end)
        if thumb_start == -1:
            pos = href_idx + 1
            continue

        thumb_end = find_div_end(tagby, thumb_start)
        if thumb_end == -1:
            pos = href_idx + 1
            continue

        if slug not in result:
            result[slug] = tagby[thumb_start:thumb_end].strip()
        pos = href_idx + 1

    return result


def make_page(thumb_html):
    # aspect-[4/3] 클래스 제거 (CSS로 고정 크기 제어)
    thumb_html = re.sub(r'\baspect-\[4/3\]\s*', '', thumb_html)
    # 카드용 inline font-size를 PNG용으로 1.5배 스케일업
    def scale_rem(m):
        val = round(float(m.group(1)) * 1.5, 3)
        return f'font-size:{val}rem'
    thumb_html = re.sub(r'font-size:([\d.]+)rem', scale_rem, thumb_html)

    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  {PRETENDARD_LINK}
  {TAILWIND_SCRIPT}
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ font-size: 20px; }}
    body {{ width: {W}px; height: {H}px; overflow: hidden; background: #000; }}
    .wrapper {{ width: {W}px; height: {H}px; }}
    .wrapper > div {{ width: {W}px !important; height: {H}px !important; }}
  </style>
</head>
<body>
  <div class="wrapper">
    {thumb_html}
  </div>
</body>
</html>"""


def main():
    with open(TAGBY_PATH, encoding='utf-8') as f:
        tagby = f.read()

    card_thumbs = extract_card_thumbnails(tagby)
    print(f"카드 썸네일 {len(card_thumbs)}개 발견")

    all_slugs = sorted(
        os.path.splitext(os.path.basename(f))[0]
        for f in glob.glob(os.path.join(ARTICLE_DIR, "*.html"))
    )

    ok, fail = 0, 0

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=DPR)

        for slug in all_slugs:
            out = os.path.join(THUM_DIR, f"{slug}.png")
            if slug not in card_thumbs:
                print(f"[SKIP] {slug} — tagby-article.html에 없음")
                fail += 1
                continue

            html_page = make_page(card_thumbs[slug])
            page.set_content(html_page, wait_until="networkidle")
            page.screenshot(path=out, clip={"x": 0, "y": 0, "width": W, "height": H})
            print(f"[OK]  {slug}.png")
            ok += 1

        browser.close()

    print(f"\n완료 — {ok} 저장 / {fail} 스킵")
    print(f"저장 위치: {THUM_DIR}")


if __name__ == "__main__":
    main()
