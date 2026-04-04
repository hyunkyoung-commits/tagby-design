# 기술 스택 및 코드 규칙

## 기술 스택
- **HTML/CSS/JS**: 순수 정적 HTML 파일 (빌드 도구 없음)
- **CSS 프레임워크**: Tailwind CSS (CDN: `https://cdn.tailwindcss.com`)
- **폰트**: Pretendard (CDN: orioncactus/pretendard@v1.3.9)
- **배포**: Vercel (GitHub 연동 자동 배포)

## 디렉토리 구조
```
/
├── *.html            # 모든 페이지 파일 (루트에 위치)
├── images/
│   ├── team profile/ # 팀원 프로필 사진 (한글 파일명 주의)
│   ├── logo/         # 브랜드 로고
│   ├── spao/         # 포트폴리오 이미지 (브랜드별 폴더)
│   ├── ...
├── design-study-article/ # 아티클 이미지
└── unused/           # 미사용 파일
```

## 주요 CSS 패턴
- 메인 컬러: `#0078F0` (TAGby 파란색)
- 배경색: `#F8F8F8`
- 폰트: Pretendard
- 드롭다운: `display:none` + `opacity:0` 기본, JS로 `display:block` + `opacity:1` 전환
- `.dropdown::after` 가상요소로 마우스 이탈 버퍼 20px 확보

## 드롭다운 JS 패턴 (모든 페이지 공통)
```javascript
(function(){
  var allDropdowns = Array.from(document.querySelectorAll('.dropdown'));
  var hideTimer; var activeMenu = null;
  function closeAll(){ ... }
  function showMenu(dropdown){ ... }
  function scheduleHide(){ hideTimer=setTimeout(closeAll,300); }
  allDropdowns.forEach(function(dropdown){ ... });
})();
```
- 공유 타이머(hideTimer)로 메뉴 간 겹침 방지
- `.dropdown`과 `.dropdown-menu` 양쪽에 mouseenter/mouseleave 이벤트 등록

## 모바일 햄버거 메뉴
- `togglePortfolioCategory(btn)` 함수로 포트폴리오 아코디언 토글
- `.category-sub` 클래스 요소에 `hidden`/`flex` 클래스 전환

## 팀 카드 스타일
- `.team-badge`: `border-radius:20px`, `font-size:10px` (pill 형태)
- 모든 뱃지 텍스트 크기: `font-size:10px`로 통일
- 카드 내 텍스트: `text-center`, `justify-center` 정렬

## 이미지 주의사항
- `images/team profile/` 폴더: 한글 파일명 + 공백 포함 → Vercel CDN에서 간헐적 로딩 오류 가능
- `onerror` 핸들러: `this.style.display='none'; this.nextElementSibling.style.display='flex';`로 플레이스홀더 표시
