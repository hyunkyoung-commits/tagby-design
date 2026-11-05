# 인기 마케팅 검색어 운영 설정

`tagby-article.html`의 인기 검색어는 Google Ads 키워드 플래너에서 제공한 월별 검색량 추정치를 사용합니다. `lib/google-keywords.js`에 선정된 마케팅 키워드를 대상으로 대한민국, 한국어, Google 검색 범위에서 조회합니다. 집계 가능한 최신 완료 월의 검색량 순으로 10개를 표시하고, 직전 월의 검색량이 양수일 때 증감률을 계산합니다.

회사 Google Cloud 프로젝트에서 Google Ads API를 활성화한 뒤, API 개요에서 키워드 플래너 조회가 가능한 Basic 또는 Standard 액세스를 승인받습니다. 같은 프로젝트에서 OAuth 클라이언트를 준비합니다. 신규 연결에 개발자 토큰은 필요하지 않습니다.

Vercel `tagby-design` 프로젝트의 **Settings → Environment Variables → Production**에 다음 값을 서버 환경 변수로 등록하고 운영 배포를 다시 실행합니다.

| 변수 | 설정 값 |
| --- | --- |
| `GOOGLE_ADS_CUSTOMER_ID` | 키워드 플래너를 조회할 Google Ads 계정 ID |
| `GOOGLE_ADS_CLIENT_ID` | Google Ads API를 사용하도록 설정한 Google Cloud OAuth 클라이언트 ID |
| `GOOGLE_ADS_CLIENT_SECRET` | 같은 OAuth 클라이언트의 비밀 키 |
| `GOOGLE_ADS_REFRESH_TOKEN` | 대상 계정에 접근할 수 있는 사용자가 `https://www.googleapis.com/auth/adwords` 범위로 승인한 갱신 토큰 |
| `GOOGLE_ADS_LOGIN_CUSTOMER_ID` | 관리자 계정 경유 시 관리자 계정 ID |
| `GOOGLE_ADS_API_VERSION` | 선택 사항. 기본값 `v25` |

재배포 후 `/api/article-list-db?resource=popular-keywords`에서 `status: ready`, 기준 월, 10개 검색어를 확인합니다. `not_configured`는 필수 값 누락, `unavailable`은 공급자 조회 실패 또는 최신 월의 수치가 있는 키워드가 10개 미만일 때 반환됩니다. 키워드와 월별 집계값만 공개 응답에 포함됩니다.

[Google Ads API 인증](https://developers.google.com/google-ads/api/docs/oauth/overview) · [월별 검색량 조회](https://developers.google.com/google-ads/api/docs/keyword-planning/generate-historical-metrics)
