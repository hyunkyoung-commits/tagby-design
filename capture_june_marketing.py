#!/usr/bin/env python3
"""
news-june-marketing-0528 아티클용 인포그래픽 PNG 생성
- compare-season-marketing.png / compare-season-marketing-light.png
"""
import os
from playwright.sync_api import sync_playwright

OUTPUT_DIR = os.path.join(
    "/Volumes/KIOXIA/작업폴더/클로드코드 워크폴더/대행사업부 웹사이트",
    "design-study-article", "news-june-marketing-0528"
)
os.makedirs(OUTPUT_DIR, exist_ok=True)

W, H = 800, 340
DPR = 2
FONT_LINK = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">'

LEFT_ITEMS  = ["기념일 맞춤 할인 프로모션", "이벤트 로고 활용 배너 광고", "단기 노출 중심 집행", "제품·가격 중심 메시지"]
RIGHT_ITEMS = ["문화·감정과 연결된 콘텐츠", "브랜드 가치 메시지 연결", "SNS·퍼포먼스·인플루언서 통합", "공감 기반 브랜드 경험 설계"]


def items_html(items, text_color):
    return "".join(f'<li style="color:{text_color};">{item}</li>' for item in items)


def build_html(box_bg, left_label_color, right_label_color, text_color, bullet_color):
    left_li  = items_html(LEFT_ITEMS, text_color)
    right_li = items_html(RIGHT_ITEMS, text_color)
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8">{FONT_LINK}
<style>
  *, *::before, *::after {{ box-sizing:border-box; margin:0; padding:0; }}
  html, body {{ width:{W}px; height:{H}px; font-family:'Pretendard',-apple-system,sans-serif; background:transparent; display:flex; }}
  .wrap {{ width:100%; height:100%; display:grid; grid-template-columns:1fr 1fr; gap:10px; }}
  .box {{ background:{box_bg}; border-radius:14px; padding:28px 32px; display:flex; flex-direction:column; justify-content:center; }}
  .lbl {{ font-size:11px; font-weight:800; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:18px; }}
  ul {{ list-style:none; padding:0; margin:0; display:flex; flex-direction:column; gap:12px; }}
  li {{ font-size:17px; font-weight:500; display:flex; align-items:center; gap:8px; }}
  li::before {{ content:'·'; color:{bullet_color}; font-size:20px; line-height:1; flex-shrink:0; }}
</style></head>
<body><div class="wrap">
  <div class="box"><p class="lbl" style="color:{left_label_color};">과거 시즌 마케팅</p><ul>{left_li}</ul></div>
  <div class="box"><p class="lbl" style="color:{right_label_color};">최근 시즌 마케팅</p><ul>{right_li}</ul></div>
</div></body></html>"""


renders = [
    ("compare-season-marketing.png",       "#222",    "#888",    "#f97316", "#ccc", "#555"),
    ("compare-season-marketing-light.png", "#f0f0f0", "#aaa",    "#e8720c", "#444", "#bbb"),
]


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=DPR)
        for filename, box_bg, left_color, right_color, text_color, bullet_color in renders:
            html = build_html(box_bg, left_color, right_color, text_color, bullet_color)
            page.set_content(html, wait_until="networkidle")
            out = os.path.join(OUTPUT_DIR, filename)
            page.screenshot(path=out, clip={"x": 0, "y": 0, "width": W, "height": H}, omit_background=True)
            print(f"[OK]  {filename}")
        browser.close()
    print(f"\n저장 위치: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
