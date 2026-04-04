# 작업 완료 시 체크리스트

## 코드 수정 후
1. 브라우저에서 로컬 확인 (Chrome 권장)
2. 모바일 뷰 확인 (반응형)
3. `git add` → `git commit` → `git push` → Vercel 자동 배포 확인

## 여러 페이지에 동일 변경 시
- Python 스크립트로 일괄 처리 (`rap_in_toggles.py` 참고 또는 즉석 스크립트 작성)
- 드롭다운 JS, 네비게이션 HTML은 모든 페이지에 동일하게 적용 필요

## 주의사항
- `.claude/` 폴더는 `.gitignore`에 등록됨 (Notion API 토큰 등 포함)
- 이미지 파일명에 한글/공백 포함 시 Vercel 서빙 문제 가능 → ASCII 파일명 권장
- `*.html.bak` 파일은 백업용으로 git에서 무시 권장
