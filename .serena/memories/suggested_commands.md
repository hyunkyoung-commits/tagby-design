# 주요 명령어

## Git / 배포
```bash
# 변경사항 커밋 & Vercel 자동 배포
git add <파일명>
git commit -m "메시지"
git push
# → Vercel이 main 브랜치 push 감지하여 자동 배포

# 여러 파일 한번에 커밋
git add *.html
git commit -m "메시지"
git push
```

## 여러 HTML 파일 일괄 수정 (Python 활용)
```python
import glob

for fname in glob.glob('*.html'):
    with open(fname, 'r') as f:
        content = f.read()
    content = content.replace('찾을텍스트', '바꿀텍스트')
    with open(fname, 'w') as f:
        f.write(content)
```

## 로컬 미리보기
- 브라우저에서 직접 HTML 파일 열기 (별도 서버 불필요)
- VSCode Live Preview는 한글 파일명 이미지를 제대로 표시 못하는 경우 있음 → Chrome 직접 열기 권장

## 이미지 경로
- 팀 프로필: `images/team profile/<이름>.png`
- 포트폴리오: `images/<브랜드>/<파일명>.png`
- 로고: `images/logo/<파일명>.png`
