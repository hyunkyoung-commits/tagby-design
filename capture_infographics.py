#!/usr/bin/env python3
"""
아티클 본문용 인포그래픽 PNG 생성 스크립트 (다크 + 라이트)
- stat-ai-search.png / stat-ai-search-light.png
- funnel-change.png  / funnel-change-light.png
- geo-checklist.png  / geo-checklist-light.png
"""
import os
from playwright.sync_api import sync_playwright

OUTPUT_DIR = os.path.join(
    "/Volumes/KIOXIA/작업폴더/클로드코드 워크폴더/대행사업부 웹사이트",
    "design-study-article", "compare-images"
)
os.makedirs(OUTPUT_DIR, exist_ok=True)

DPR = 2
FONT_LINK = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">'
BASE_STYLE = "*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; } body { font-family: 'Pretendard', -apple-system, sans-serif; background: transparent; }"


# ── 공통 데이터 ───────────────────────────────────────────────────────────────
STAT_W, STAT_H   = 1200, 270
FUNNEL_W, FUNNEL_H = 1200, 420
CHECK_W, CHECK_H = 1200, 300

ITEMS = [
    "AI가 이해하기 쉬운 문장 구조",
    "질문 기반 콘텐츠 구성",
    "결론을 먼저 제시하는 구조",
    "신뢰 가능한 출처 명시",
    "헤딩·리스트로 구조화된 정보",
    "브랜드 관련 사실 정보 명시",
]


# ── 체크리스트 아이템 HTML 빌더 ───────────────────────────────────────────────
def checklist_items(text_color):
    check_svg = '<svg width="13" height="10" viewBox="0 0 13 10" fill="none"><polyline points="1,5 5,9 12,1" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    return "".join(f"""
  <div style="display:flex;align-items:center;gap:14px;">
    <div style="width:22px;height:22px;border-radius:5px;background:#6366f1;display:flex;align-items:center;justify-content:center;flex-shrink:0;">{check_svg}</div>
    <span style="font-size:18px;font-weight:500;color:{text_color};">{item}</span>
  </div>""" for item in ITEMS)


# ── 퍼널 스텝 HTML 빌더 ───────────────────────────────────────────────────────
def funnel_steps(steps, dot_color, line_color, text_color):
    html = ""
    for i, s in enumerate(steps):
        is_last = i == len(steps) - 1
        line = "" if is_last else f'<div style="width:2px;height:26px;background:{line_color};margin:0 auto;"></div>'
        html += f"""
        <div style="display:flex;align-items:flex-start;gap:16px;">
          <div style="display:flex;flex-direction:column;align-items:center;width:28px;flex-shrink:0;">
            <div style="width:10px;height:10px;border-radius:50%;background:{dot_color};flex-shrink:0;margin-top:6px;"></div>
            {line}
          </div>
          <span style="font-size:20px;font-weight:600;color:{text_color};padding:2px 0;">{s}</span>
        </div>"""
    return html


# ══ DARK 버전 ════════════════════════════════════════════════════════════════

STAT_DARK = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">{FONT_LINK}
<style>{BASE_STYLE}
  html,body{{width:{STAT_W}px;height:{STAT_H}px;display:flex;align-items:center;justify-content:center;}}
  .wrap{{width:1120px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;}}
  .card{{background:#222;border-radius:16px;padding:28px 32px;display:flex;flex-direction:column;gap:6px;}}
  .platform{{font-size:11px;font-weight:800;letter-spacing:0.12em;text-transform:uppercase;}}
  .number{{font-size:46px;font-weight:900;line-height:1.05;}}
  .desc{{font-size:15px;font-weight:500;color:#bbb;margin-top:4px;}}
  .source{{font-size:11px;color:#444;margin-top:10px;}}
</style></head><body>
<div class="wrap">
  <div class="card"><p class="platform" style="color:#0ea5e9;">ChatGPT</p><p class="number" style="color:#0ea5e9;">약 10억</p><p class="desc">월간 활성 사용자</p><p class="source">OpenAI 발표, 2026년 2월 기준</p></div>
  <div class="card"><p class="platform" style="color:#6366f1;">Google AI Overviews</p><p class="number" style="color:#6366f1;">약 20억</p><p class="desc">월간 사용자</p><p class="source">Google 발표, 2025년 말 기준</p></div>
  <div class="card"><p class="platform" style="color:#10b981;">Google AI Mode</p><p class="number" style="color:#10b981;">1억+</p><p class="desc">월간 활성 사용자</p><p class="source">Google 발표, 2026년 기준</p></div>
</div></body></html>"""

_fl = funnel_steps(["검색","클릭","랜딩","구매"], "#555", "#333", "#aaa")
_fr = funnel_steps(["질문","AI 답변","추천","액션"], "#0ea5e9", "rgba(14,165,233,0.2)", "#fff")
FUNNEL_DARK = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">{FONT_LINK}
<style>{BASE_STYLE}
  html,body{{width:{FUNNEL_W}px;height:{FUNNEL_H}px;display:flex;align-items:center;justify-content:center;}}
  .wrap{{width:1120px;display:grid;grid-template-columns:1fr 1fr;gap:20px;}}
  .side{{background:#222;border-radius:16px;padding:36px 44px;}}
  .lbl{{font-size:12px;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:28px;}}
</style></head><body>
<div class="wrap">
  <div class="side"><p class="lbl" style="color:#666;">기존 검색 퍼널</p>{_fl}</div>
  <div class="side"><p class="lbl" style="color:#0ea5e9;">AI 검색 퍼널</p>{_fr}</div>
</div></body></html>"""

CHECKLIST_DARK = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">{FONT_LINK}
<style>{BASE_STYLE}
  html,body{{width:{CHECK_W}px;height:{CHECK_H}px;display:flex;align-items:center;justify-content:center;}}
</style></head><body>
<div style="width:1120px;background:#222;border-radius:16px;padding:36px 48px;">
  <p style="font-size:12px;font-weight:800;letter-spacing:0.12em;text-transform:uppercase;color:#6366f1;margin-bottom:28px;">GEO 콘텐츠 최적화 체크리스트</p>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px 48px;">{checklist_items("#ccc")}</div>
</div></body></html>"""


# ══ LIGHT 버전 ═══════════════════════════════════════════════════════════════

STAT_LIGHT = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">{FONT_LINK}
<style>{BASE_STYLE}
  html,body{{width:{STAT_W}px;height:{STAT_H}px;display:flex;align-items:center;justify-content:center;}}
  .wrap{{width:1120px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;}}
  .card{{background:#f0f0f0;border-radius:16px;padding:28px 32px;display:flex;flex-direction:column;gap:6px;}}
  .platform{{font-size:11px;font-weight:800;letter-spacing:0.12em;text-transform:uppercase;}}
  .number{{font-size:46px;font-weight:900;line-height:1.05;}}
  .desc{{font-size:15px;font-weight:500;color:#555;margin-top:4px;}}
  .source{{font-size:11px;color:#aaa;margin-top:10px;}}
</style></head><body>
<div class="wrap">
  <div class="card"><p class="platform" style="color:#0284c7;">ChatGPT</p><p class="number" style="color:#0284c7;">약 10억</p><p class="desc">월간 활성 사용자</p><p class="source">OpenAI 발표, 2026년 2월 기준</p></div>
  <div class="card"><p class="platform" style="color:#4f46e5;">Google AI Overviews</p><p class="number" style="color:#4f46e5;">약 20억</p><p class="desc">월간 사용자</p><p class="source">Google 발표, 2025년 말 기준</p></div>
  <div class="card"><p class="platform" style="color:#059669;">Google AI Mode</p><p class="number" style="color:#059669;">1억+</p><p class="desc">월간 활성 사용자</p><p class="source">Google 발표, 2026년 기준</p></div>
</div></body></html>"""

_fll = funnel_steps(["검색","클릭","랜딩","구매"], "#bbb", "#e0e0e0", "#888")
_frl = funnel_steps(["질문","AI 답변","추천","액션"], "#0284c7", "rgba(2,132,199,0.2)", "#111")
FUNNEL_LIGHT = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">{FONT_LINK}
<style>{BASE_STYLE}
  html,body{{width:{FUNNEL_W}px;height:{FUNNEL_H}px;display:flex;align-items:center;justify-content:center;}}
  .wrap{{width:1120px;display:grid;grid-template-columns:1fr 1fr;gap:20px;}}
  .side{{background:#f0f0f0;border-radius:16px;padding:36px 44px;}}
  .lbl{{font-size:12px;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:28px;}}
</style></head><body>
<div class="wrap">
  <div class="side"><p class="lbl" style="color:#aaa;">기존 검색 퍼널</p>{_fll}</div>
  <div class="side"><p class="lbl" style="color:#0284c7;">AI 검색 퍼널</p>{_frl}</div>
</div></body></html>"""

CHECKLIST_LIGHT = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">{FONT_LINK}
<style>{BASE_STYLE}
  html,body{{width:{CHECK_W}px;height:{CHECK_H}px;display:flex;align-items:center;justify-content:center;}}
</style></head><body>
<div style="width:1120px;background:#f0f0f0;border-radius:16px;padding:36px 48px;">
  <p style="font-size:12px;font-weight:800;letter-spacing:0.12em;text-transform:uppercase;color:#4f46e5;margin-bottom:28px;">GEO 콘텐츠 최적화 체크리스트</p>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px 48px;">{checklist_items("#444")}</div>
</div></body></html>"""


# ── 렌더링 ────────────────────────────────────────────────────────────────────
renders = [
    ("stat-ai-search.png",        STAT_W,   STAT_H,   STAT_DARK),
    ("funnel-change.png",         FUNNEL_W, FUNNEL_H, FUNNEL_DARK),
    ("geo-checklist.png",         CHECK_W,  CHECK_H,  CHECKLIST_DARK),
    ("stat-ai-search-light.png",  STAT_W,   STAT_H,   STAT_LIGHT),
    ("funnel-change-light.png",   FUNNEL_W, FUNNEL_H, FUNNEL_LIGHT),
    ("geo-checklist-light.png",   CHECK_W,  CHECK_H,  CHECKLIST_LIGHT),
]

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for filename, w, h, html in renders:
            page = browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=DPR)
            page.set_content(html, wait_until="networkidle")
            out = os.path.join(OUTPUT_DIR, filename)
            page.screenshot(path=out, clip={"x": 0, "y": 0, "width": w, "height": h}, omit_background=True)
            print(f"[OK]  {filename}")
        browser.close()
    print(f"\n저장 위치: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
