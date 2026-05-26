#!/usr/bin/env python3
"""
모든 아티클에 OG 태그 + canonical 태그 추가 & sitemap.xml 재생성
"""
import os, re, json, glob

BASE = "/Volumes/KIOXIA/작업폴더/클로드코드 워크폴더/대행사업부 웹사이트"
ARTICLE_DIR = os.path.join(BASE, "design-study-article")
SITEMAP_PATH = os.path.join(BASE, "sitemap.xml")
SITE_URL = "https://mkt.tagby.io"

# 날짜 추출: 파일명 끝 -MMDD 패턴 → 2026-MM-DD
def slug_to_date(slug):
    m = re.search(r'-(\d{2})(\d{2})$', slug)
    if m:
        mm, dd = m.group(1), m.group(2)
        return f"2026-{mm}-{dd}"
    # 날짜 없는 오래된 파일들
    date_map = {
        "news-instagram-algorithm": "2026-01-28",
        "news-threads-ads": "2026-01-20",
        "news-youtube-shopping": "2026-01-15",
        "news-tiktok-search-ads": "2026-01-08",
        "news-pmax-brand": "2025-12-20",
        "news-naver-ai-bidding": "2025-12-15",
        "news-meta-advantage": "2026-02-10",
        "news-google-ai": "2026-02-15",
        "content-influencer-roi": "2026-02-20",
        "content-branded-vs-native": "2026-02-22",
        "content-naver-seo": "2026-02-25",
        "content-fandom-marketing": "2026-02-28",
        "content-viral-reels": "2026-03-04",
        "content-email-marketing": "2026-03-07",
        "content-kakao-crm": "2026-03-11",
        "content-youtube-strategy": "2026-02-18",
        "content-shortform-roi-0223": "2026-02-23",
        "design-figma-2025": "2026-02-22",
        "design-ux-writing": "2026-02-17",
        "design-ui-trends-2025": "2026-02-10",
        "design-adobe-firefly": "2026-02-05",
        "design-color-system": "2026-01-28",
        "design-typography": "2026-01-22",
        "design-dark-mode": "2026-01-15",
        "design-responsive-web": "2026-01-10",
        "news-may-ecommerce": "2026-05-01",
        "newsletter-ad-formula": "2026-04-21",
        "newsletter-ai-creative": "2026-04-20",
        "newsletter-performance-trend": "2026-04-10",
        "newsletter-q2-calendar": "2026-04-05",
        "newsletter-ss-trend": "2026-03-28",
        "article-1209": "2025-12-09",
        "article-1210": "2025-12-10",
    }
    return date_map.get(slug, "2026-01-01")


def extract_ld_fields(html):
    """JSON-LD에서 Article 타입의 headline, description, url 추출"""
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
    if not m:
        return None, None, None
    try:
        data = json.loads(m.group(1))
        graph = data.get("@graph", [])
        for node in graph:
            if node.get("@type") == "Article":
                return (
                    node.get("headline", ""),
                    node.get("description", ""),
                    node.get("url", ""),
                )
    except Exception:
        pass
    return None, None, None


def build_og_block(title, description, url, slug):
    img_url = f"{SITE_URL}/design-study-article/thum/{slug}.png"
    # description 길이 제한 (160자)
    desc = description[:160] if description else title
    return f"""  <meta property="og:type" content="article">
  <meta property="og:site_name" content="TAGby">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{img_url}">
  <meta property="og:image:width" content="1000">
  <meta property="og:image:height" content="750">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{desc}">
  <meta name="twitter:image" content="{img_url}">
  <link rel="canonical" href="{url}">"""


def process_article(filepath):
    slug = os.path.splitext(os.path.basename(filepath))[0]
    with open(filepath, encoding="utf-8") as f:
        html = f.read()

    # 이미 OG 태그 있으면 스킵
    if 'property="og:title"' in html:
        print(f"[SKIP] {slug} — 이미 OG 태그 있음")
        return None

    title, description, url = extract_ld_fields(html)
    if not title:
        print(f"[WARN] {slug} — JSON-LD 파싱 실패, <title> 태그 사용")
        m = re.search(r'<title>(.*?)</title>', html)
        title = m.group(1) if m else slug
        description = title
        url = f"{SITE_URL}/design-study-article/{slug}.html"

    og_block = build_og_block(title, description, url, slug)

    # </head> 바로 앞에 삽입
    new_html = html.replace("</head>", f"{og_block}\n</head>", 1)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_html)

    print(f"[OK]  {slug}")
    return (slug, url)


# 기존 sitemap 핵심 페이지 (아티클 제외)
SITEMAP_HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">

  <!-- 핵심 페이지 -->
  <url><loc>https://mkt.tagby.io/</loc><lastmod>2026-05-17</lastmod><changefreq>weekly</changefreq><priority>1.0</priority></url>
  <url><loc>https://mkt.tagby.io/about.html</loc><lastmod>2026-04-21</lastmod><changefreq>monthly</changefreq><priority>0.9</priority></url>
  <url><loc>https://mkt.tagby.io/portfolio.html</loc><lastmod>2026-04-21</lastmod><changefreq>monthly</changefreq><priority>0.9</priority></url>
  <url><loc>https://mkt.tagby.io/tagby-article.html</loc><lastmod>2026-05-17</lastmod><changefreq>weekly</changefreq><priority>0.9</priority></url>

  <!-- 서비스 -->
  <url><loc>https://mkt.tagby.io/performance-marketing.html</loc><lastmod>2026-04-21</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>
  <url><loc>https://mkt.tagby.io/influencer-marketing.html</loc><lastmod>2026-04-21</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>

  <!-- 팀 소개 -->
  <url><loc>https://mkt.tagby.io/team-performance.html</loc><lastmod>2026-04-21</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>
  <url><loc>https://mkt.tagby.io/team-digital.html</loc><lastmod>2026-04-21</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>
  <url><loc>https://mkt.tagby.io/team-design.html</loc><lastmod>2026-04-21</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>

  <!-- 브랜드 포트폴리오 -->
  <url><loc>https://mkt.tagby.io/spao.html</loc><lastmod>2026-04-21</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>
  <url><loc>https://mkt.tagby.io/mixxo.html</loc><lastmod>2026-04-21</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>
  <url><loc>https://mkt.tagby.io/newbalance.html</loc><lastmod>2026-04-21</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>
  <url><loc>https://mkt.tagby.io/spaokids.html</loc><lastmod>2026-04-21</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>
  <url><loc>https://mkt.tagby.io/roem.html</loc><lastmod>2026-04-21</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>
  <url><loc>https://mkt.tagby.io/eider.html</loc><lastmod>2026-04-21</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>
  <url><loc>https://mkt.tagby.io/eblin.html</loc><lastmod>2026-04-21</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>
  <url><loc>https://mkt.tagby.io/cocodor.html</loc><lastmod>2026-04-21</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>
  <url><loc>https://mkt.tagby.io/emart.html</loc><lastmod>2026-04-21</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>
  <url><loc>https://mkt.tagby.io/minbyoungcheol.html</loc><lastmod>2026-04-21</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>

"""


def update_sitemap(article_entries):
    """article_entries: list of (slug, date, priority)"""
    lines = [SITEMAP_HEADER, "  <!-- 아티클 전체 -->\n"]
    for slug, date, priority in sorted(article_entries, key=lambda x: x[1], reverse=True):
        url = f"{SITE_URL}/design-study-article/{slug}.html"
        lines.append(f'  <url><loc>{url}</loc><lastmod>{date}</lastmod><changefreq>never</changefreq><priority>{priority}</priority></url>\n')
    lines.append("\n</urlset>\n")
    with open(SITEMAP_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"\n[sitemap] {len(article_entries)}개 아티클 → sitemap.xml 업데이트 완료")


def main():
    html_files = sorted(glob.glob(os.path.join(ARTICLE_DIR, "*.html")))
    print(f"총 {len(html_files)}개 아티클 처리 시작\n")

    article_entries = []
    for filepath in html_files:
        slug = os.path.splitext(os.path.basename(filepath))[0]
        process_article(filepath)
        date = slug_to_date(slug)
        # TAGby Original은 priority 0.7, 나머지 0.6
        priority = "0.7" if slug.startswith("newsletter") or slug.startswith("article-") else "0.6"
        article_entries.append((slug, date, priority))

    update_sitemap(article_entries)
    print("\n모든 작업 완료!")


if __name__ == "__main__":
    main()
