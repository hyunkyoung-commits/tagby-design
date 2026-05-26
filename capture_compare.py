#!/usr/bin/env python3
"""
비교 박스(compare-box)를 PNG 이미지로 렌더링하는 스크립트
compare_boxes 리스트에 내용 추가하면 재사용 가능
"""
import os
from playwright.sync_api import sync_playwright

OUTPUT_DIR = os.path.join(
    "/Volumes/KIOXIA/작업폴더/클로드코드 워크폴더/대행사업부 웹사이트",
    "design-study-article", "compare-images"
)
os.makedirs(OUTPUT_DIR, exist_ok=True)

W, H = 1200, 480
DPR = 2

# ── 렌더링할 비교 박스 목록 ──────────────────────────────────────────────────
# left_color, right_color: CSS color 값
# items: 리스트 항목들
compare_boxes = [
    {
        "filename": "compare-search-vs-ai.png",
        "left_label": "기존 검색",
        "left_color": "#888",
        "left_items": ["키워드를 검색한다", "검색 결과를 비교한다", "여러 사이트를 클릭한다", "정보를 종합해 판단한다"],
        "right_label": "AI 검색",
        "right_color": "#0ea5e9",
        "right_items": ["질문을 입력한다", "AI가 정리한 답변을 확인한다", "추천 브랜드를 인식한다", "바로 액션으로 이동한다"],
    },
    {
        "filename": "compare-seo-vs-geo.png",
        "left_label": "기존 SEO",
        "left_color": "#888",
        "left_items": ["키워드 최적화", "메타 태그", "백링크", "클릭률 확보", "콘텐츠 분량 확보"],
        "right_label": "GEO (AI 시대)",
        "right_color": "#6366f1",
        "right_items": ["AI가 이해하기 쉬운 문장 구조", "질문 기반 콘텐츠", "명확한 결론", "신뢰 가능한 출처", "구조화된 정보"],
    },
]
# ────────────────────────────────────────────────────────────────────────────


def build_html(box):
    left_items_html = "".join(f"<li>{item}</li>" for item in box["left_items"])
    right_items_html = "".join(f"<li>{item}</li>" for item in box["right_items"])

    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body {{
      width: {W}px; height: {H}px;
      background: transparent;
      font-family: 'Pretendard', -apple-system, sans-serif;
      display: flex; align-items: center; justify-content: center;
    }}
    .wrap {{
      width: {W - 80}px;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }}
    .box {{
      background: #222;
      border-radius: 16px;
      padding: 36px 40px;
    }}
    .label {{
      font-size: 13px;
      font-weight: 800;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      margin-bottom: 24px;
    }}
    ul {{
      list-style: none;
      padding: 0;
      margin: 0;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}
    li {{
      font-size: 20px;
      font-weight: 500;
      color: #ccc;
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    li::before {{
      content: '·';
      color: #555;
      font-size: 22px;
      line-height: 1;
      flex-shrink: 0;
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="box">
      <p class="label" style="color:{box['left_color']};">{box['left_label']}</p>
      <ul>{left_items_html}</ul>
    </div>
    <div class="box">
      <p class="label" style="color:{box['right_color']};">{box['right_label']}</p>
      <ul>{right_items_html}</ul>
    </div>
  </div>
</body>
</html>"""


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=DPR)

        for box in compare_boxes:
            html = build_html(box)
            page.set_content(html, wait_until="networkidle")
            out = os.path.join(OUTPUT_DIR, box["filename"])
            page.screenshot(path=out, clip={"x": 0, "y": 0, "width": W, "height": H}, omit_background=True)
            print(f"[OK]  {box['filename']}")

        browser.close()

    print(f"\n저장 위치: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
