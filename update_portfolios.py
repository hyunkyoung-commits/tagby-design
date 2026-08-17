#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
포트폴리오 페이지 신규 이미지 업데이트 스크립트
대상: spao.html, mixxo.html, roem.html, minbyoungcheol.html, cocodor.html
"""
import re
import urllib.parse
from pathlib import Path

BASE = Path("/Volumes/KIOXIA/작업폴더/클로드코드 워크폴더/대행사업부 웹사이트")

def enc(fn):
    return urllib.parse.quote(fn, safe='')

def extract_date(fn):
    m = re.search(r'(\d{2}\.\d{2})', fn)
    return m.group(1) if m else '00.00'

def date_kr(d):
    yy, mm = d.split('.')
    return f"{yy}년 {int(mm)}월"

def get_title(fn):
    name = Path(fn).stem
    name = re.sub(r'^\d+\.\s+', '', name)           # "5. " 제거
    name = re.sub(r'^(\[.*?\])+', '', name)           # [AI][Meta] 등 제거
    name = re.sub(r'\(\d{2}\.\d{2}\)', '', name)      # (26.05) 제거
    name = re.sub(r'_단일\(\d{2}\.\d{2}\)$', '', name)
    name = re.sub(r'^\d{2}\.\d{2}_', '', name)        # 26.05_ 접두사 제거
    name = re.sub(r'\s+-\d+$', '', name)              # " -1" 시리즈 번호 제거
    return name.strip()

def group_series(filenames):
    """
    -N 번호 파일들을 캐러셀 그룹으로 묶고, 날짜 내림차순 정렬
    Returns: [(type, [fns]), ...]  type = 'single' | 'carousel'
    """
    from collections import OrderedDict
    series_map = OrderedDict()
    singles = []

    for fn in filenames:
        m = re.match(r'^(.*?)\s+-(\d+)(\.[^.]+)$', fn)
        if m:
            base = m.group(1)
            if base not in series_map:
                series_map[base] = []
            series_map[base].append((int(m.group(2)), fn))
        else:
            singles.append(fn)

    def sort_key(fn):
        d = extract_date(fn)
        yy, mm = d.split('.')
        return (-int(yy), -int(mm), fn)

    all_groups = []
    for base, items in series_map.items():
        items.sort()
        first = items[0][1]
        all_groups.append((sort_key(first), 'carousel', [fn for _, fn in items]))
    for fn in singles:
        all_groups.append((sort_key(fn), 'single', [fn]))

    all_groups.sort(key=lambda x: x[0])
    return [(t, fns) for _, t, fns in all_groups]

# ── 갤러리 아이템 HTML 생성 헬퍼 ────────────────────────────

OERR = "this.parentElement.style.background='#E5EAF0';this.style.display='none'"

def item_multiline(idx, fn, folder, brand, date_str, title, visible):
    hidden = '' if visible else ' hidden'
    return f"""        <div class="gallery-item fade-in{hidden}" data-index="{idx}">
          <img loading="lazy" src="images/portfolio/{folder}/{enc(fn)}" alt="{brand} {title}" onerror="{OERR}">
          <div class="gallery-overlay">
            <div class="gallery-info">
              <p class="text-white text-sm mb-1 font-medium">{brand}</p>
              <p class="text-white/70 text-xs mb-2">{date_str}</p>
              <p class="text-white text-lg font-bold">{title}</p>
            </div>
          </div>
        </div>"""

def item_compact(idx, fn, folder, brand, date_str, title, visible):
    hidden = '' if visible else ' hidden'
    return f"""        <div class="gallery-item fade-in{hidden}" data-index="{idx}">
          <img loading="lazy" src="images/portfolio/{folder}/{enc(fn)}" alt="{brand} {title}" onerror="{OERR}">
          <div class="gallery-overlay"><div class="gallery-info"><p class="text-white text-sm mb-1 font-medium">{brand}</p><p class="text-white/70 text-xs mb-2">{date_str}</p><p class="text-white text-lg font-bold">{title}</p></div></div>
        </div>"""

def carousel_multiline(idx, fns, folder, brand, page_id, date_str, title, visible):
    hidden = '' if visible else ' hidden'
    cid = f'carousel-{page_id}-{idx}'
    imgs = '\n'.join(
        f'            <img loading="lazy" src="images/portfolio/{folder}/{enc(fn)}" '
        f'alt="{brand} {get_title(fn)}" onerror="{OERR}">'
        for fn in fns
    )
    dots = '\n'.join(
        f'            <span class="carousel-dot{" active" if i==0 else ""}" '
        f'onclick="carouselGoto(\'{cid}\', {i}, event)"></span>'
        for i in range(len(fns))
    )
    return f"""        <div class="gallery-item fade-in carousel-item{hidden}" data-index="{idx}" style="cursor:default;">
          <div class="carousel-track" id="{cid}">
{imgs}
          </div>
          <button class="carousel-btn carousel-prev" onclick="carouselMove('{cid}', -1, event)">&#8249;</button>
          <button class="carousel-btn carousel-next" onclick="carouselMove('{cid}', 1, event)">&#8250;</button>
          <div class="carousel-dots" id="dots-{cid}">
{dots}
          </div>
          <div class="gallery-overlay">
            <div class="gallery-info">
              <p class="text-white text-sm mb-1 font-medium">{brand}</p>
              <p class="text-white/70 text-xs mb-2">{date_str}</p>
              <p class="text-white text-lg font-bold">{title}</p>
            </div>
          </div>
        </div>"""

def find_gallery_bounds(html):
    """gallery-grid div의 내용 범위 반환: (전체시작, 내용시작, 내용끝, 전체끝)"""
    marker = '<div class="gallery-grid" id="galleryGrid">'
    start = html.find(marker)
    if start == -1:
        raise ValueError("gallery-grid not found")
    cs = start + len(marker)
    depth = 1
    pos = cs
    while depth > 0 and pos < len(html):
        no = html.find('<div', pos)
        nc = html.find('</div>', pos)
        if nc == -1:
            break
        if no != -1 and no < nc:
            depth += 1
            pos = no + 4
        else:
            depth -= 1
            if depth == 0:
                return start, cs, nc, nc + 6
            pos = nc + 6
    raise ValueError("closing div not found")

# ── 캐러셀 CSS/JS (ROEM용) ───────────────────────────────────

CAROUSEL_CSS = """    .carousel-item { overflow: hidden; }
    .carousel-item::before { opacity: 1 !important; }
    .carousel-track { display: flex; width: 100%; height: 100%; transition: transform 0.35s cubic-bezier(0.4,0,0.2,1); }
    .carousel-track img { flex: 0 0 100%; width: 100%; height: 100%; object-fit: contain; background: transparent; position: relative !important; z-index: 2 !important; transform: none !important; transition: none !important; }
    .carousel-btn {
      position: absolute; top: 50%; transform: translateY(-50%); z-index: 4;
      background: rgba(0,0,0,0.45); backdrop-filter: blur(4px); border: none;
      color: white; font-size: 24px; width: 36px; height: 36px; border-radius: 50%;
      display: flex; align-items: center; justify-content: center; cursor: pointer;
      opacity: 0; transition: opacity 0.2s ease; line-height: 1;
    }
    .gallery-item:hover .carousel-btn { opacity: 1; }
    .carousel-prev { left: 10px; }
    .carousel-next { right: 10px; }
    .carousel-dots { position: absolute; bottom: 10px; left: 50%; transform: translateX(-50%); z-index: 4; display: flex; gap: 5px; }
    .carousel-dot { width: 6px; height: 6px; border-radius: 50%; background: rgba(255,255,255,0.5); cursor: pointer; transition: background 0.2s; }
    .carousel-dot.active { background: white; }"""

CAROUSEL_JS = """    var carouselState = {};
    function updateCarouselBg(id) {
      var track = document.getElementById(id);
      if (!track) return;
      var imgs = track.querySelectorAll('img');
      var idx = carouselState[id] || 0;
      var src = imgs[idx] ? imgs[idx].getAttribute('src') : '';
      var item = track.closest('.gallery-item');
      if (item && src) item.style.backgroundImage = "url('" + src + "')";
    }
    function carouselMove(id, dir, e) {
      if (e) e.stopPropagation();
      var track = document.getElementById(id);
      if (!track) return;
      var total = track.querySelectorAll('img').length;
      if (!carouselState[id]) carouselState[id] = 0;
      carouselState[id] = (carouselState[id] + dir + total) % total;
      track.style.transform = 'translateX(-' + (carouselState[id] * 100) + '%)';
      updateDots(id, total);
      updateCarouselBg(id);
    }
    function carouselGoto(id, idx, e) {
      if (e) e.stopPropagation();
      var track = document.getElementById(id);
      if (!track) return;
      var total = track.querySelectorAll('img').length;
      carouselState[id] = idx;
      track.style.transform = 'translateX(-' + (idx * 100) + '%)';
      updateDots(id, total);
      updateCarouselBg(id);
    }
    function updateDots(id, total) {
      var dotsEl = document.getElementById('dots-' + id);
      if (!dotsEl) return;
      dotsEl.querySelectorAll('.carousel-dot').forEach(function(d, i) {
        d.classList.toggle('active', i === carouselState[id]);
      });
    }
    document.querySelectorAll('.carousel-item').forEach(function(item) {
      var track = item.querySelector('.carousel-track');
      if (!track) return;
      var firstImg = track.querySelector('img');
      if (firstImg) item.style.backgroundImage = "url('" + firstImg.getAttribute('src') + "')";
    });"""

# ════════════════════════════════════════════════════════════
# SPAO: 신규 7개 (26.05) 아이템을 앞에 삽입, 기존 인덱스 +7 쉬프트
# ════════════════════════════════════════════════════════════
def update_spao():
    html_path = BASE / "spao.html"
    html = html_path.read_text(encoding='utf-8')

    new_files = [
        "[AI][Meta](26.05)cool festa.jpg",
        "[AI][Meta](26.05)sheer wind breaker.jpg",
        "[Meta](26.05)cool festa.jpg",
        "[Meta](26.05)members week.jpg",
        "[Meta](26.05)sleeveless pajama.jpg",
        "[Meta](26.05)summer shirts.jpg",
        "[Meta](26.05)summer shirts2.jpg",
    ]
    N = len(new_files)  # 7

    # 기존 인덱스 0-45를 7씩 올리고 visible→hidden 처리 (높은 것부터)
    for old in range(45, -1, -1):
        new_i = old + N
        if old < 6:
            # 기존에 visible → 이제 hidden (인덱스 7-12)
            html = html.replace(
                f'<div class="gallery-item fade-in" data-index="{old}">',
                f'<div class="gallery-item fade-in hidden" data-index="{new_i}">'
            )
        else:
            html = html.replace(
                f'<div class="gallery-item fade-in hidden" data-index="{old}">',
                f'<div class="gallery-item fade-in hidden" data-index="{new_i}">'
            )

    # 신규 아이템 HTML 생성 (0-5 visible, 6 hidden)
    new_items = []
    for i, fn in enumerate(new_files):
        date = extract_date(fn)
        title = get_title(fn)
        html_item = item_multiline(i, fn, "spao", "SPAO", date, title, i < 6)
        new_items.append(html_item)

    insert_html = '\n\n'.join(new_items)
    html = html.replace(
        '<div class="gallery-grid" id="galleryGrid">',
        '<div class="gallery-grid" id="galleryGrid">\n\n' + insert_html + '\n\n'
    )

    html_path.write_text(html, encoding='utf-8')
    print(f"✓ SPAO: {N}개 신규 아이템 추가 (총 {N + 46}개)")

# ════════════════════════════════════════════════════════════
# MIXXO: 전체 갤러리 재구성 (12개, 첫 6개 visible)
# ════════════════════════════════════════════════════════════
def update_mixxo():
    html_path = BASE / "mixxo.html"
    html = html_path.read_text(encoding='utf-8')

    # 폴더 내 전체 파일 (날짜 내림차순 정렬)
    all_files = [
        ("[AI][Meta](26.05)SummerEssential.jpg",  "SummerEssential"),
        ("[AI][Meta](26.05)WeekendSale.jpg",       "WeekendSale"),
        ("[Meta](26.04)blossom week.jpg",           "Blossom Week"),
        ("[Meta](26.04)Always top.jpg",             "Always Top"),
        ("[Meta](26.04)Always pants.jpg",           "Always Pants"),
        ("[Meta]8. 메타4_카우걸_단일(25.09).jpg",   "카우걸"),
        ("[Meta]7. 메타2_카우걸_단일(25.09).jpg",   "카우걸 2"),
        ("[Meta]6. 메타8_뉴시즌 뉴스타트_화보&제품강조_단일(25.09).jpg", "뉴시즌 뉴스타트"),
        ("[Meta]5. 메타6_미쏘데이(당일)_단일(25.08).jpg", "미쏘데이"),
        ("[Meta]3. 메타5_핀터걸_단일(25.07).jpg",   "핀터걸"),
        ("[Meta]2. 메타3_레이어드_단일(25.04).jpg",  "레이어드 2"),
        ("[Meta]1. 메타5_레이어드_단일(25.04).jpg",  "레이어드 1"),
    ]

    items_html = []
    for i, (fn, title) in enumerate(all_files):
        date = extract_date(fn)
        date_str = date_kr(date)
        visible = i < 6
        items_html.append(item_multiline(i, fn, "mixxo", "MIXXO", date_str, title, visible))

    new_content = '\n\n'.join(items_html)
    start, cs, ce, end = find_gallery_bounds(html)
    html = html[:cs] + '\n\n' + new_content + '\n\n      ' + html[ce:]

    html_path.write_text(html, encoding='utf-8')
    print(f"✓ MIXXO: {len(all_files)}개로 재구성")

# ════════════════════════════════════════════════════════════
# ROEM: 전체 재구성 + 캐러셀 추가 (은채X영로엠 컬렉션 -1/-2/-3)
# ════════════════════════════════════════════════════════════
def update_roem():
    html_path = BASE / "roem.html"
    html = html_path.read_text(encoding='utf-8')

    all_files = [
        "[Meta](26.05)은채X영로엠 컬렉션 -1.jpg",
        "[Meta](26.05)은채X영로엠 컬렉션 -2.jpg",
        "[Meta](26.05)은채X영로엠 컬렉션 -3.jpg",
        "[Meta](26.05)SALE 기획전.jpg",
        "[Meta](26.05)6월 전마.jpg",
        "[Meta](26.04)ROEM BRANDDAY.jpg",
        "[Meta](26.04)ROEM WEEK.jpg",
        "[Meta](26.04)Summer Campaign.jpg",
        "[Meta](26.04)뉴캐리오버.jpg",
        "[Meta](26.04)로엠위크.jpg",
        "[Meta](26.04)무드위크.jpg",
        "[Meta](26.04)브랜드데이.jpg",
        "[Meta](26.04)썸머큐레이션.jpg",
        "[Meta](26.04)5월전마.jpg",
        "[Meta](26.03) 신상 첫 공개.jpg",
        "[Meta](26.03) 로엠위크.jpg",
        "[Meta](26.01)10-1 메타-온라인 단독 아우터.jpg",
        "[Meta](26.01)9-1 메타-온라인 단독 아우터.jpg",
        "[Meta](26.01)8-1 메타-윈터 트렌드.jpg",
        "[Meta](26.01)5-1 메타-윈터 트렌드.jpg",
        "[Meta](26.01)3-1 메타-온라인 단독 아우터.jpg",
        "[Meta](25.12) LAST SEASON OFF SALE.jpg",
        "[Meta](25.11)7-1 메타_브랜드위크.jpg",
        "[Meta](25.11)3-1 메타_홀리데이.jpg",
        "[Meta](25.10)3-1 메타_출근룩.jpg",
    ]

    groups = group_series(all_files)

    # 캐러셀 CSS 삽입
    if 'carousel-item' not in html:
        html = html.replace('  </style>', CAROUSEL_CSS + '\n  </style>')

    items_html = []
    for i, (typ, fns) in enumerate(groups):
        visible = i < 6
        date = extract_date(fns[0])
        title = get_title(fns[0])
        if typ == 'carousel':
            items_html.append(carousel_multiline(i, fns, "roem", "ROEM", "roem", date, title, visible))
        else:
            items_html.append(item_multiline(i, fns[0], "roem", "ROEM", date, title, visible))

    new_content = '\n\n'.join(items_html)
    start, cs, ce, end = find_gallery_bounds(html)
    html = html[:cs] + '\n\n' + new_content + '\n\n      ' + html[ce:]

    # 캐러셀 JS 삽입 (마지막 </script> 바로 앞)
    if 'function carouselMove' not in html:
        last = html.rfind('</script>')
        if last != -1:
            html = html[:last] + CAROUSEL_JS + '\n  ' + html[last:]

    html_path.write_text(html, encoding='utf-8')
    print(f"✓ ROEM: {len(groups)}개로 재구성 (캐러셀 포함, 중복 제거)")

# ════════════════════════════════════════════════════════════
# MINBYOUNGCHEOL: 신규 2개 (26.05) 앞에 삽입
# ════════════════════════════════════════════════════════════
def update_minbyoungcheol():
    html_path = BASE / "minbyoungcheol.html"
    html = html_path.read_text(encoding='utf-8')

    new_files = [
        ("[AI][Meta](26.05)RE.jpg",               "RE"),
        ("[AI][Remember](26.05)EnglishRoutin.jpg", "English Routine"),
    ]
    N = len(new_files)  # 2

    # 기존 인덱스 0-10 처리 (높은 것부터)
    for old in range(10, -1, -1):
        new_i = old + N
        if old < 6:
            if old < 4:
                # 여전히 visible (new_i = 2-5)
                html = html.replace(
                    f'<div class="gallery-item fade-in" data-index="{old}">',
                    f'<div class="gallery-item fade-in" data-index="{new_i}">'
                )
            else:
                # visible → hidden (new_i = 6,7)
                html = html.replace(
                    f'<div class="gallery-item fade-in" data-index="{old}">',
                    f'<div class="gallery-item fade-in hidden" data-index="{new_i}">'
                )
        else:
            html = html.replace(
                f'<div class="gallery-item fade-in hidden" data-index="{old}">',
                f'<div class="gallery-item fade-in hidden" data-index="{new_i}">'
            )

    new_items = []
    for i, (fn, title) in enumerate(new_files):
        date = extract_date(fn)
        date_str = date_kr(date)
        # compact 형식
        new_items.append(item_compact(i, fn, "minbyoungcheol", "민병철유폰", date_str, title, True))

    insert_html = '\n'.join(new_items)
    html = html.replace(
        '<div class="gallery-grid" id="galleryGrid">',
        '<div class="gallery-grid" id="galleryGrid">\n' + insert_html + '\n'
    )

    html_path.write_text(html, encoding='utf-8')
    print(f"✓ MINBYOUNGCHEOL: {N}개 신규 아이템 추가 (총 {N + 11}개)")

# ════════════════════════════════════════════════════════════
# COCODOR: 전체 재구성 (20개)
# ════════════════════════════════════════════════════════════
def update_cocodor():
    html_path = BASE / "cocodor.html"
    html = html_path.read_text(encoding='utf-8')

    all_files = [
        # 26.05 신규
        ("[AI][Meta](26.05)상시 그란데디퓨저 영상.png", "상시 그란데디퓨저"),
        ("[AI][Meta](26.05)상시 리필액.png",            "상시 리필액"),
        ("[Meta](26.05)상시 리필.png",                  "상시 리필"),
        ("[Meta](26.05)상시 샤쉐.png",                  "상시 샤쉐"),
        ("[Naver](26.05)상시 차량용우드볼.jpg",          "상시 차량용우드볼"),
        # 26.04 (신규 + 기존)
        ("[AI][Meta](26.04)상시 샤쉐 영상.png",         "상시 샤쉐 영상"),
        ("[Kakao](26.04)BEST4.jpg",                     "BEST4"),
        ("[Kakao](26.04)뉴레이어에디션.jpg",            "뉴레이어 에디션"),
        ("[Kakao](26.04)신상품 기획전.jpg",             "신상품 기획전"),
        ("[Meta](26.04)상시 샤쉐.png",                  "상시 샤쉐 (Meta)"),
        ("[Meta](26.04)상시 섬유탈취제.png",            "상시 섬유탈취제"),
        ("[Naver](26.04)가정의달.jpg",                  "가정의달"),
        # 26.02 기존
        ("8. 26.02_퍼퓸샤쉐.png",                      "퍼퓸샤쉐"),
        ("7. 26.02_퍼퓸샤쉐 2.png",                    "퍼퓸샤쉐 2"),
        ("6. 26.02_차량용 방향제.png",                  "차량용 방향제"),
        ("5. 26.02_섬유탈취제.png",                     "섬유탈취제"),
        ("4. 26.02_디퓨저 대량구매.png",                "디퓨저 대량구매"),
        # 26.01 기존
        ("3. 26.01_시그니처 컬렉션.png",                "시그니처 컬렉션"),
        ("2. 26.01_설날프로모션.png",                   "설날 프로모션"),
        # 25.10 기존
        ("1. 25.10_양재동꽃시장.jpg",                   "양재동꽃시장 디퓨저"),
    ]

    items_html = []
    for i, (fn, title) in enumerate(all_files):
        date = extract_date(fn)
        date_str = date_kr(date)
        visible = i < 6
        items_html.append(item_compact(i, fn, "cocodor", "코코도르", date_str, title, visible))

    new_content = '\n\n'.join(items_html)
    start, cs, ce, end = find_gallery_bounds(html)
    html = html[:cs] + '\n' + new_content + '\n      ' + html[ce:]

    html_path.write_text(html, encoding='utf-8')
    print(f"✓ COCODOR: {len(all_files)}개로 재구성")

# ════════════════════════════════════════════════════════════

if __name__ == '__main__':
    update_spao()
    update_mixxo()
    update_roem()
    update_minbyoungcheol()
    update_cocodor()
    print("\n✅ 모든 업데이트 완료!")
