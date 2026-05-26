#!/usr/bin/env python3
import os

BASE = "/Volumes/KIOXIA/작업폴더/클로드코드 워크폴더/대행사업부 웹사이트"
ARTICLE_DIR = os.path.join(BASE, "design-study-article")

# (main_text, subtitle, gradient)
ARTICLES = {
    'news-ai-ops-strategy-0506':  ('Ad Ops', 'AI 자동화 전략', '#2a0f60 0%,#0d0020 100%'),
    'content-ugc-trust-0421':     ('UGC', '브랜드 2.5배 신뢰도', '#e65c00 0%,#f7971e 100%'),
    'design-ai-tools-figma-0417': ('AI Design Wars', 'Claude · Stitch · Figma', '#302b63 0%,#0f0c29 100%'),
    'news-fullfunnel-0421':       ('풀펀넬', '브랜드가 놓치는 중간 구간', '#16213e 0%,#0f3460 100%'),
    'news-digital-weekly-0421':   ('April Update', 'Google · Meta · TikTok · LinkedIn', '#1a73e8 0%,#7b2ff7 100%'),
    'news-pmax-april-0421':       ('PMax', 'Microsoft · ROAS 600%', '#0078d4 0%,#005a9e 100%'),
    'content-digital-apr-0421':   ('April 2026', '디지털 마케팅 현황', '#3498db 0%,#2c3e50 100%'),
    'content-startup-april-0421': ('스타트업', 'AI 개인화 콘텐츠 마케팅', '#11998e 0%,#1a3a38 100%'),
    'content-kakao-crm':          ('카카오', 'CRM 마케팅 가이드', '#fee500 0%,#f0c800 100%'),
    'content-email-marketing':    ('이메일 마케팅', '오픈율 2배 전략', '#8E54E9 0%,#4776E6 100%'),
    'content-viral-reels':        ('릴스·쇼츠', '바이럴 공식', '#f953c6 0%,#b91d73 100%'),
    'content-fandom-marketing':   ('팬덤 마케팅', '브랜드 커뮤니티 구축', '#c471ed 0%,#f64f59 100%'),
    'content-naver-seo':          ('네이버 SEO', '블로그 최적화 전략', '#03c75a 0%,#0a3320 100%'),
    'content-shortform-roi-0223': ('숏폼 ROI', '49% · 라이브 24배', '#f953c6 0%,#b91d73 100%'),
    'content-branded-vs-native':  ('브랜디드 콘텐츠', 'vs 네이티브 광고', '#0f3460 0%,#1a1a2e 100%'),
    'design-figma-2025':          ('Figma', '2025 핵심 기능 총정리', '#7B61FF 0%,#1a0a3d 100%'),
    'content-influencer-roi':     ('인플루언서 ROI', '효과 측정 방법', '#f7971e 0%,#ffd200 100%'),
    'content-youtube-strategy':   ('YouTube', '채널 성장 전략 5가지', '#ff4e50 0%,#f9d423 100%'),
    'design-ux-writing':          ('UX Writing', '버튼 문구와 전환율', '#667eea 0%,#764ba2 100%'),
    'news-perf-stop-guessing-0421': ('STOP', 'Guessing · 2026 퍼포먼스', '#0f2027 0%,#2c5364 100%'),
    'news-google-ai':             ('Google', 'AI Overview 광고 영향', '#1a73e8 0%,#0d47a1 100%'),
    'news-meta-advantage':        ('Meta A+', 'Advantage+ ROAS 개선', '#0866ff 0%,#7b2ff7 100%'),
    'design-ui-trends-2025':      ('UI Trends', '2025 모바일 디자인', '#0078F0 0%,#00c6ff 100%'),
    'design-adobe-firefly':       ('Adobe Firefly', 'AI 기능 실무 활용법', '#FF0000 0%,#003087 100%'),
    'news-instagram-algorithm':   ('Instagram', '2025 알고리즘 업데이트', '#f09433 0%,#bc1888 100%'),
    'design-color-system':        ('컬러 시스템', 'Primary부터 Semantic까지', '#20bf6b 0%,#0078F0 100%'),
    'design-typography':          ('타이포그래피', '자간·행간·여백 가이드', '#2c3e50 0%,#3498db 100%'),
    'news-threads-ads':           ('Threads', '광고 베타 공식 시작', '#1c1c1c 0%,#000000 100%'),
    'news-perf-playbook-0421':    ('Playbook 2026', 'AI · 속도 · 수익성', '#0f2027 0%,#2c5364 100%'),
    'news-youtube-shopping':      ('YouTube', '쇼핑 광고 강화', '#212121 0%,#cc0000 100%'),
    'design-dark-mode':           ('Dark Mode', 'UI 설계 가이드', '#111111 0%,#2d2d2d 100%'),
    'design-responsive-web':      ('반응형 웹', '디자인 체크리스트 20', '#2c3e50 0%,#3498db 100%'),
    'news-tiktok-search-ads':     ('TikTok', '검색 광고 정식 출시', '#010101 0%,#fe2c55 100%'),
    'news-pmax-brand':            ('PMax', '브랜드 키워드 제어', '#0f2027 0%,#2c5364 100%'),
    'news-naver-ai-bidding':      ('NAVER', 'AI 자동입찰 전면 확대', '#03c75a 0%,#0a3320 100%'),
}


def find_div_end(content, start):
    """Find the closing </div> for a div that starts at 'start', handling nesting."""
    pos = start
    depth = 0
    while pos < len(content):
        next_open = content.find('<div', pos)
        next_close = content.find('</div>', pos)
        if next_close == -1:
            break
        if next_open == -1:
            next_open = len(content)
        if next_open < next_close:
            depth += 1
            pos = next_open + 4
        else:
            depth -= 1
            pos = next_close + 6
            if depth == 0:
                return pos
    return -1


def make_article_thumb(main, sub, colors):
    return (
        f'      <div class="mb-12 rounded-2xl overflow-hidden" '
        f'style="background:linear-gradient(135deg,{colors});'
        f'aspect-ratio:16/9;display:flex;align-items:center;justify-content:center;">\n'
        f'        <div class="text-center">\n'
        f'          <p class="text-white font-black" style="font-size:2rem;letter-spacing:0.02em;">{main}</p>\n'
        f'          <p class="text-white text-sm tracking-widest mt-2">{sub}</p>\n'
        f'        </div>\n'
        f'      </div>'
    )


def make_card_thumb(main, sub, colors):
    return (
        f'          <div class="aspect-[4/3] flex items-center justify-center" '
        f'style="background:linear-gradient(135deg,{colors});">\n'
        f'            <div class="text-center">\n'
        f'              <p class="text-white font-black" style="font-size:2rem;letter-spacing:0.02em;">{main}</p>\n'
        f'              <p class="text-white text-sm tracking-widest mt-2">{sub}</p>\n'
        f'            </div>\n'
        f'          </div>'
    )


# ── 1. Update individual article pages ────────────────────────────────────────
article_ok = 0
article_fail = 0
for slug, (main, sub, colors) in ARTICLES.items():
    path = os.path.join(ARTICLE_DIR, f"{slug}.html")
    if not os.path.exists(path):
        print(f"[SKIP] {slug} — file not found")
        article_fail += 1
        continue

    with open(path, encoding='utf-8') as f:
        content = f.read()

    ac_idx = content.find('<div class="article-content">')
    if ac_idx == -1:
        print(f"[SKIP] {slug} — no article-content div")
        article_fail += 1
        continue

    before = content[:ac_idx]
    t12 = before.rfind('<div class="mb-12')
    t14 = before.rfind('<div class="mb-14')
    thumb_start = max(t12, t14)
    if thumb_start == -1:
        print(f"[SKIP] {slug} — no mb-12/mb-14 thumbnail")
        article_fail += 1
        continue

    thumb_end = find_div_end(content, thumb_start)
    if thumb_end == -1:
        print(f"[SKIP] {slug} — could not find thumbnail end")
        article_fail += 1
        continue

    new_content = content[:thumb_start] + make_article_thumb(main, sub, colors) + '\n' + content[thumb_end:]
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"[OK]   article: {slug}")
    article_ok += 1


# ── 2. Update card thumbnails in tagby-article.html ───────────────────────────
tagby_path = os.path.join(BASE, "tagby-article.html")
with open(tagby_path, encoding='utf-8') as f:
    tagby = f.read()

card_ok = 0
card_fail = 0
for slug, (main, sub, colors) in ARTICLES.items():
    href = f'href="design-study-article/{slug}.html"'
    href_idx = tagby.find(href)
    if href_idx == -1:
        print(f"[SKIP] card {slug} — href not found")
        card_fail += 1
        continue

    # Find the next card's href to limit search scope
    next_href_idx = tagby.find('<a href="design-study-article/', href_idx + len(href))
    scope_end = next_href_idx if next_href_idx != -1 else href_idx + 3000

    # Find aspect-[4/3] div within this card
    thumb_start = tagby.find('<div class="aspect-[4/3]', href_idx, scope_end)
    if thumb_start == -1:
        # Also try the TAGby-Original format (aspect-[4/3] without flex)
        thumb_start = tagby.find('<div class="aspect-[4/3]"', href_idx, scope_end)
    if thumb_start == -1:
        print(f"[SKIP] card {slug} — no aspect-[4/3] div")
        card_fail += 1
        continue

    thumb_end = find_div_end(tagby, thumb_start)
    if thumb_end == -1:
        print(f"[SKIP] card {slug} — could not find card thumbnail end")
        card_fail += 1
        continue

    tagby = tagby[:thumb_start] + make_card_thumb(main, sub, colors) + tagby[thumb_end:]
    print(f"[OK]   card:    {slug}")
    card_ok += 1

with open(tagby_path, 'w', encoding='utf-8') as f:
    f.write(tagby)

print(f"\nDone — articles: {article_ok} ok / {article_fail} fail | cards: {card_ok} ok / {card_fail} fail")
