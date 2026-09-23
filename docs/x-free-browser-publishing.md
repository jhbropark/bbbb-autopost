# X 브라우저 handoff

X 게시의 공식 자동 경로는 `scripts/meta_publish.py`의 X API adapter입니다. GitHub Actions는 OAuth 1.0a 또는 OAuth 2.0 설정이 있으면 API 게시를 시도합니다.

동시에 `x-browser-handoff.html`도 생성합니다. 이 파일은 API를 사용할 수 없거나 계정 소유자가 브라우저에서 최종 검토하고 싶을 때 사용하는 수동 fallback입니다.

## 일일 흐름

1. GitHub Actions가 콘텐츠, 이미지, `x-browser-handoff.html`을 생성합니다.
2. 기본 경로는 `meta_publish.py`를 통한 X API 게시입니다.
3. API 게시가 불가능하면 Pages의 handoff 페이지를 엽니다.
4. 본문을 검토하고 X composer를 엽니다.
5. 이미지 형식이면 PNG를 첨부합니다.
6. Thread 형식이면 첫 게시물 이후 각 항목을 답글로 게시합니다.

handoff 페이지는 텍스트만 채우며 이미지 첨부와 최종 Post 클릭은 사용자가 직접 수행합니다.

## 로컬 handoff 생성

```powershell
python .\scripts\x_browser_handoff.py `
  --caption .\artifacts\2026-09-22-mechanism-in-motion\x-post.txt `
  --thread .\artifacts\2026-09-22-mechanism-in-motion\x-thread.txt `
  --carousel-dir .\artifacts\2026-09-22-mechanism-in-motion\carousel `
  --out .\artifacts\2026-09-22-mechanism-in-motion\x-browser-handoff.html
```

브라우저 게시를 사용할 때도 이 저장소의 자동 게시 엔진은 `meta_publish.py`로 유지합니다. handoff는 별도 게시 시스템이 아니라 검토 가능한 보조 산출물입니다.
