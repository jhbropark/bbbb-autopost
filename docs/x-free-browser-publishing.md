# X 무료 게시 경로

X API 크레딧을 사용하지 않는 경로입니다. GitHub Actions는 콘텐츠와 X 게시 핸드오프 페이지를 만들고 GitHub Pages에 배포합니다. 게시 행위는 계정 소유자가 로그인한 X 브라우저에서 최종 실행합니다.

이 구분은 의도적입니다. GitHub-hosted runner에는 개인 X 브라우저 세션이 없으며, 웹 UI의 자동 클릭으로 이를 우회하지 않습니다.

## 일일 흐름

1. GitHub Actions가 콘텐츠, 이미지, `x-browser-handoff.html`을 생성합니다.
2. 배포된 Pages 경로의 `x-browser-handoff.html`을 엽니다.
3. 본문을 검토하고 `Open X composer` 또는 `Copy text`를 사용합니다.
4. 이미지 형식이면 표시된 PNG 파일을 첨부합니다.
5. 스레드 형식이면 01을 게시한 뒤 02부터 순서대로 답글로 게시합니다.

핸드오프 페이지는 `intent/post` 링크를 이용해 **텍스트만** 채웁니다. 이미지 첨부와 최종 `Post` 클릭은 X 웹 UI에서 사용자가 직접 수행합니다.

## 로컬 생성 및 확인

```powershell
python .\scripts\x_browser_handoff.py `
  --caption .\artifacts\2026-06-19-beauty-myth-lab\x-post.txt `
  --thread .\artifacts\2026-06-19-beauty-myth-lab\x-thread.txt `
  --carousel-dir .\artifacts\2026-06-19-beauty-myth-lab\carousel `
  --out .\artifacts\2026-06-19-beauty-myth-lab\x-browser-handoff.html
```

API 게시를 다시 사용하려면 X Developer Console에 크레딧을 충전한 뒤 기존 OAuth 1.0a 비밀값을 유지하면 됩니다. 이 무료 경로는 API 게시 실패와 무관하게 계속 사용할 수 있습니다.
