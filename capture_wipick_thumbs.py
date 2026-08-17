#!/usr/bin/env python3
"""
위픽레터용 밈 스타일 썸네일 시안 3종 생성
저장 위치: wipick-thumbnails/
"""
import os, base64
from playwright.sync_api import sync_playwright

BASE   = "/Volumes/KIOXIA/작업폴더/클로드코드 워크폴더/대행사업부 웹사이트"
OUTDIR = os.path.join(BASE, "wipick-thumbnails")
FONT   = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">'

W, H = 1200, 630
DPR  = 2


def b64img(filename):
    path = os.path.join(OUTDIR, filename)
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    ext = "jpeg"
    return f"data:image/{ext};base64,{data}"


# ─── 시안 1: 드레이크 밈 ───────────────────────────────────────────────────
# 왼쪽: Drake 이미지 / 오른쪽: 거절 vs 승인 텍스트
def html_drake():
    img = b64img("base-drake.jpg")
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8">{FONT}
<style>
  *{{margin:0;padding:0;box-sizing:border-box;}}
  body{{width:{W}px;height:{H}px;display:flex;background:#111;font-family:'Pretendard',-apple-system,sans-serif;overflow:hidden;}}
  .meme{{width:480px;height:{H}px;flex-shrink:0;background:url('{img}') top center/cover;}}
  .right{{flex:1;display:flex;flex-direction:column;justify-content:center;padding:48px 44px;gap:20px;}}
  .no{{background:#c0392b;border-radius:12px;padding:24px 28px;}}
  .yes{{background:#27ae60;border-radius:12px;padding:24px 28px;}}
  .label{{font-size:13px;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:10px;opacity:0.7;color:white;}}
  .text{{font-size:26px;font-weight:800;color:white;line-height:1.35;}}
  .footer{{margin-top:28px;font-size:14px;color:#666;font-weight:600;letter-spacing:0.05em;}}
</style></head>
<body>
  <div class="meme"></div>
  <div class="right">
    <div class="no">
      <p class="label">❌ 이건 좀...</p>
      <p class="text">입찰가 수동으로 올렸다<br>내렸다 하는 마케터</p>
    </div>
    <div class="yes">
      <p class="label">✅ 이게 맞지</p>
      <p class="text">AI한테 최적화 맡기고<br>크리에이티브나 고민함</p>
    </div>
    <p class="footer">2026 퍼포먼스 마케터의 현실 체크</p>
  </div>
</body></html>"""


# ─── 시안 2: This is Fine 🔥 ───────────────────────────────────────────────
def html_thisisfine():
    img = b64img("base-thisisfine.jpg")
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8">{FONT}
<style>
  *{{margin:0;padding:0;box-sizing:border-box;}}
  body{{width:{W}px;height:{H}px;position:relative;font-family:'Pretendard',-apple-system,sans-serif;overflow:hidden;background:#000;}}
  .bg{{position:absolute;inset:0;background:url('{img}') center/cover;filter:brightness(0.45) saturate(1.4);}}
  .overlay{{position:relative;z-index:1;width:100%;height:100%;display:flex;flex-direction:column;justify-content:center;align-items:center;padding:60px;text-align:center;}}
  .tag{{background:#e74c3c;color:white;font-size:13px;font-weight:800;letter-spacing:0.12em;text-transform:uppercase;padding:8px 20px;border-radius:100px;margin-bottom:28px;}}
  .main{{font-size:54px;font-weight:900;color:white;line-height:1.15;text-shadow:0 3px 12px rgba(0,0,0,0.8);margin-bottom:20px;}}
  .sub{{font-size:30px;font-weight:700;color:#FFD700;text-shadow:0 2px 8px rgba(0,0,0,0.9);line-height:1.4;}}
</style></head>
<body>
  <div class="bg"></div>
  <div class="overlay">
    <div class="tag">🔥 ROAS가 30% 떨어졌다</div>
    <p class="main">"괜찮아..."</p>
    <p class="sub">자동화가 알아서<br>해줄 거야 🐶</p>
  </div>
</body></html>"""


# ─── 시안 3: 곁눈질하는 남자친구 밈 ──────────────────────────────────────
def html_distracted():
    img = b64img("base-distracted.jpg")
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8">{FONT}
<style>
  *{{margin:0;padding:0;box-sizing:border-box;}}
  body{{width:{W}px;height:{H}px;position:relative;font-family:'Pretendard',-apple-system,sans-serif;overflow:hidden;background:#000;}}
  .bg{{position:absolute;inset:0;background:url('{img}') center/cover;filter:brightness(0.55);}}
  .overlay{{position:relative;z-index:1;width:100%;height:100%;}}
  .label{{position:absolute;background:rgba(0,0,0,0.75);color:white;font-weight:800;border-radius:8px;padding:8px 16px;font-size:16px;border:2px solid white;}}
  .label-guy{{top:44%;left:62%;transform:translateX(-50%);font-size:15px;color:#ffd700;border-color:#ffd700;background:rgba(0,0,0,0.85);}}
  .label-new{{top:18%;right:5%;font-size:14px;color:#ff6b6b;border-color:#ff6b6b;}}
  .label-gf{{top:44%;left:7%;font-size:14px;color:#74b9ff;border-color:#74b9ff;}}
  .bottom{{position:absolute;bottom:0;left:0;right:0;background:linear-gradient(to top,rgba(0,0,0,0.95) 0%,rgba(0,0,0,0) 100%);padding:28px 40px 36px;}}
  .bottom-text{{font-size:32px;font-weight:900;color:white;line-height:1.3;}}
  .bottom-sub{{font-size:18px;color:#aaa;margin-top:8px;font-weight:600;}}
</style></head>
<body>
  <div class="bg"></div>
  <div class="overlay">
    <div class="label label-guy">😵 마케터</div>
    <div class="label label-new">AI 자동화 툴 ✨</div>
    <div class="label label-gf">직접 수동 세팅 😤</div>
    <div class="bottom">
      <p class="bottom-text">2026 퍼포먼스 마케터<br>하반기 생존 전략 🚀</p>
      <p class="bottom-sub">자동화 시대, 마케터가 집중해야 할 것</p>
    </div>
  </div>
</body></html>"""


def main():
    renders = [
        ("wipick-01-drake.png",      html_drake()),
        ("wipick-02-thisisfine.png", html_thisisfine()),
        ("wipick-03-distracted.png", html_distracted()),
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=DPR)
        for filename, html in renders:
            page.set_content(html, wait_until="networkidle")
            out = os.path.join(OUTDIR, filename)
            page.screenshot(path=out, clip={"x": 0, "y": 0, "width": W, "height": H})
            print(f"[OK]  {filename}")
        browser.close()

    print(f"\n저장 위치: {OUTDIR}")


if __name__ == "__main__":
    main()
