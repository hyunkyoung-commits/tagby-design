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
    "design-study-article", "content-ai-seo-0521"
)
os.makedirs(OUTPUT_DIR, exist_ok=True)

DPR = 2
FONT_LINK = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">'

# 아티클 실제 표시 폭 ~720px → 800px 캔버스, 여백 없이 full-bleed
STAT_W,   STAT_H   = 800, 185
FUNNEL_W, FUNNEL_H = 800, 215
CHECK_W,  CHECK_H  = 800, 270

ITEMS = [
    "AI가 이해하기 쉬운 문장 구조",
    "질문 기반 콘텐츠 구성",
    "결론을 먼저 제시하는 구조",
    "신뢰 가능한 출처 명시",
    "헤딩·리스트로 구조화된 정보",
    "브랜드 관련 사실 정보 명시",
]

BASE = "*, *::before, *::after {{ box-sizing:border-box; margin:0; padding:0; }} body {{ font-family:'Pretendard',-apple-system,sans-serif; background:transparent; }}"


# ── 빌더 함수 ─────────────────────────────────────────────────────────────────
def checklist_items(text_color):
    svg = '<svg width="13" height="10" viewBox="0 0 13 10" fill="none"><polyline points="1,5 5,9 12,1" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    return "".join(f"""
  <div style="display:flex;align-items:center;gap:12px;">
    <div style="width:20px;height:20px;border-radius:4px;background:#6366f1;display:flex;align-items:center;justify-content:center;flex-shrink:0;">{svg}</div>
    <span style="font-size:16px;font-weight:500;color:{text_color};">{item}</span>
  </div>""" for item in ITEMS)


def funnel_steps(steps, dot, line, text):
    html = ""
    for i, s in enumerate(steps):
        is_last = i == len(steps) - 1
        connector = "" if is_last else f'<div style="width:2px;height:22px;background:{line};margin:0 auto;"></div>'
        html += f"""
        <div style="display:flex;align-items:flex-start;gap:14px;">
          <div style="display:flex;flex-direction:column;align-items:center;width:24px;flex-shrink:0;">
            <div style="width:9px;height:9px;border-radius:50%;background:{dot};flex-shrink:0;margin-top:5px;"></div>
            {connector}
          </div>
          <span style="font-size:18px;font-weight:600;color:{text};padding:1px 0;">{s}</span>
        </div>"""
    return html


def html_wrap(W, H, inner_css, body_html):
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8">{FONT_LINK}
<style>
  {BASE.format()}
  html, body {{ width:{W}px; height:{H}px; display:flex; }}
  {inner_css}
</style></head><body>{body_html}</body></html>"""


# ══ DARK 버전 ════════════════════════════════════════════════════════════════

STAT_DARK = html_wrap(STAT_W, STAT_H,
    """.wrap{width:100%;height:100%;display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;}
       .card{background:#222;border-radius:14px;padding:24px 28px;display:flex;flex-direction:column;gap:5px;justify-content:center;}
       .platform{font-size:11px;font-weight:800;letter-spacing:0.12em;text-transform:uppercase;}
       .number{font-size:44px;font-weight:900;line-height:1.05;}
       .desc{font-size:14px;font-weight:500;color:#bbb;margin-top:3px;}
       .source{font-size:11px;color:#444;margin-top:8px;}""",
    """<div class="wrap">
  <div class="card"><p class="platform" style="color:#0ea5e9;">ChatGPT</p><p class="number" style="color:#0ea5e9;">약 10억</p><p class="desc">월간 활성 사용자</p><p class="source">OpenAI 발표, 2026년 2월 기준</p></div>
  <div class="card"><p class="platform" style="color:#6366f1;">Google AI Overviews</p><p class="number" style="color:#6366f1;">약 20억</p><p class="desc">월간 사용자</p><p class="source">Google 발표, 2025년 말 기준</p></div>
  <div class="card"><p class="platform" style="color:#10b981;">Google AI Mode</p><p class="number" style="color:#10b981;">1억+</p><p class="desc">월간 활성 사용자</p><p class="source">Google 발표, 2026년 기준</p></div>
</div>""")

_fd_l = funnel_steps(["검색","클릭","랜딩","구매"], "#555", "#333", "#aaa")
_fd_r = funnel_steps(["질문","AI 답변","추천","액션"], "#0ea5e9", "rgba(14,165,233,0.2)", "#fff")
FUNNEL_DARK = html_wrap(FUNNEL_W, FUNNEL_H,
    """.wrap{width:100%;height:100%;display:grid;grid-template-columns:1fr 1fr;gap:10px;}
       .side{background:#222;border-radius:14px;padding:22px 32px;display:flex;flex-direction:column;justify-content:center;}
       .lbl{font-size:11px;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:20px;}""",
    f"""<div class="wrap">
  <div class="side"><p class="lbl" style="color:#666;">기존 검색 퍼널</p>{_fd_l}</div>
  <div class="side"><p class="lbl" style="color:#0ea5e9;">AI 검색 퍼널</p>{_fd_r}</div>
</div>""")

_ci_dark = checklist_items("#ccc")
CHECKLIST_DARK = html_wrap(CHECK_W, CHECK_H,
    "",
    f"""<div style="width:100%;height:100%;background:#222;border-radius:14px;padding:28px 36px;display:flex;flex-direction:column;justify-content:center;">
  <p style="font-size:11px;font-weight:800;letter-spacing:0.12em;text-transform:uppercase;color:#6366f1;margin-bottom:20px;">GEO 콘텐츠 최적화 체크리스트</p>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px 40px;">{_ci_dark}</div>
</div>""")


# ══ LIGHT 버전 ═══════════════════════════════════════════════════════════════

STAT_LIGHT = html_wrap(STAT_W, STAT_H,
    """.wrap{width:100%;height:100%;display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;}
       .card{background:#f0f0f0;border-radius:14px;padding:24px 28px;display:flex;flex-direction:column;gap:5px;justify-content:center;}
       .platform{font-size:11px;font-weight:800;letter-spacing:0.12em;text-transform:uppercase;}
       .number{font-size:44px;font-weight:900;line-height:1.05;}
       .desc{font-size:14px;font-weight:500;color:#555;margin-top:3px;}
       .source{font-size:11px;color:#aaa;margin-top:8px;}""",
    """<div class="wrap">
  <div class="card"><p class="platform" style="color:#0284c7;">ChatGPT</p><p class="number" style="color:#0284c7;">약 10억</p><p class="desc">월간 활성 사용자</p><p class="source">OpenAI 발표, 2026년 2월 기준</p></div>
  <div class="card"><p class="platform" style="color:#4f46e5;">Google AI Overviews</p><p class="number" style="color:#4f46e5;">약 20억</p><p class="desc">월간 사용자</p><p class="source">Google 발표, 2025년 말 기준</p></div>
  <div class="card"><p class="platform" style="color:#059669;">Google AI Mode</p><p class="number" style="color:#059669;">1억+</p><p class="desc">월간 활성 사용자</p><p class="source">Google 발표, 2026년 기준</p></div>
</div>""")

_fl_l = funnel_steps(["검색","클릭","랜딩","구매"], "#bbb", "#e0e0e0", "#888")
_fl_r = funnel_steps(["질문","AI 답변","추천","액션"], "#0284c7", "rgba(2,132,199,0.2)", "#111")
FUNNEL_LIGHT = html_wrap(FUNNEL_W, FUNNEL_H,
    """.wrap{width:100%;height:100%;display:grid;grid-template-columns:1fr 1fr;gap:10px;}
       .side{background:#f0f0f0;border-radius:14px;padding:22px 32px;display:flex;flex-direction:column;justify-content:center;}
       .lbl{font-size:11px;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:20px;}""",
    f"""<div class="wrap">
  <div class="side"><p class="lbl" style="color:#aaa;">기존 검색 퍼널</p>{_fl_l}</div>
  <div class="side"><p class="lbl" style="color:#0284c7;">AI 검색 퍼널</p>{_fl_r}</div>
</div>""")

_ci_light = checklist_items("#444")
CHECKLIST_LIGHT = html_wrap(CHECK_W, CHECK_H,
    "",
    f"""<div style="width:100%;height:100%;background:#f0f0f0;border-radius:14px;padding:28px 36px;display:flex;flex-direction:column;justify-content:center;">
  <p style="font-size:11px;font-weight:800;letter-spacing:0.12em;text-transform:uppercase;color:#4f46e5;margin-bottom:20px;">GEO 콘텐츠 최적화 체크리스트</p>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px 40px;">{_ci_light}</div>
</div>""")


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
