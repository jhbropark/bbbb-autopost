# bbbb-autopost

GitHub Actions 기반의 일일 콘텐츠 생성·다중 채널 게시 파이프라인입니다.

공식 게시 경로는 다음 두 파일을 중심으로 동작합니다.

- 워크플로: [.github/workflows/daily-social-publish.yml](.github/workflows/daily-social-publish.yml)
- 게시 엔진: [scripts/meta_publish.py](scripts/meta_publish.py)

구형 단일 게시 CLI인 `social_publisher.py`는 제거했습니다. 로컬 검증이 필요하면 동일한 `meta_publish.py`를 `--dry-run`으로 사용합니다.

## 처리 흐름

1. 주제별 이미지 소싱: Pexels → Pixabay → OpenAI
2. 날짜 기반 주제 선택
3. 5장 PNG/JPG 캐러셀 생성
4. Instagram Reel MP4 생성
5. GitHub Pages에 공개 미디어 배포
6. 공개 이미지·영상 URL 검증
7. Instagram cooldown 및 중복 캡션 검사
8. 채널별 공식 API 게시
9. 채널별 게시 결과 JSON을 Actions artifact로 저장

## 지원 채널

- Instagram: 이미지 캐러셀, Reel
- Facebook Page: 다중 이미지 게시
- LinkedIn: 5장 다중 이미지 게시
- X: 텍스트, 이미지, Thread
- Reddit: 이미지 URL을 포함한 self post

X 브라우저 handoff HTML도 생성하지만 자동 게시의 기본 경로는 X API입니다. API 실패 시 handoff 파일을 브라우저에서 검토해 수동 게시할 수 있습니다.

## GitHub Actions 설정

1. Repository Settings → Pages에서 Source를 GitHub Actions로 설정합니다.
2. [docs/github-actions-setup.md](docs/github-actions-setup.md)의 Secrets를 등록합니다.
3. `daily-social-publish.yml`을 수동 실행하거나 매일 예약 실행합니다.

수동 실행 입력값:

- `dry_run=true`: 생성·검증만 수행
- `publish_scope`: `all`, `instagram`, `instagram_reel`, `facebook`, `linkedin`, `linkedin_en`, `x`, `reddit`

## 로컬 dry-run

환경변수를 설정한 뒤 생성된 콘텐츠 패키지를 대상으로 실행합니다. 실제 게시를 하지 않고 입력 파일과 공개 URL만 검증합니다.

`meta_publish.py`는 다음 입력을 사용합니다.

`--carousel-dir`, `--public-base-url`, `--instagram-caption`, `--facebook-caption`, `--linkedin-caption`, `--x-caption`, `--reddit-title`, `--reddit-post`

예시:

```powershell
python .\scripts\meta_publish.py `
  --carousel-dir .\artifacts\2026-09-22-mechanism-in-motion\carousel `
  --public-base-url https://example.github.io/bbbb-autopost/social/test/content `
  --instagram-caption .\artifacts\2026-09-22-mechanism-in-motion\instagram-caption.txt `
  --facebook-caption .\artifacts\2026-09-22-mechanism-in-motion\facebook-caption.txt `
  --linkedin-caption .\artifacts\2026-09-22-mechanism-in-motion\linkedin-post.txt `
  --x-caption .\artifacts\2026-09-22-mechanism-in-motion\x-post.txt `
  --reddit-title .\artifacts\2026-09-22-mechanism-in-motion\reddit-title.txt `
  --reddit-post .\artifacts\2026-09-22-mechanism-in-motion\reddit-post.txt `
  --channels instagram,facebook,linkedin,x,reddit `
  --out .\artifacts\publish-results.json `
  --dry-run
```

실제 게시에서는 `--dry-run`을 제거합니다. Instagram Reel은 `--channels instagram_reel`, `--instagram-reel-url`, `--instagram-reel-caption`을 함께 사용해야 합니다.

## 게시 결과 해석

게시 엔진은 채널별 결과 또는 오류를 JSON으로 기록합니다. Actions 단계가 성공해도 `--allow-failures`가 사용된 게시 단계는 일부 채널 오류를 결과 JSON에만 기록할 수 있으므로 artifact를 함께 확인해야 합니다.

## 정책과 중복 방지

- `config/content_policy.json`: 비활성화할 콘텐츠 pillar
- `scripts/validate_publish_policy.py`: 시각 소스·Instagram caption 검증
- `scripts/instagram_cooldown.py`: Instagram 활동 제한 cooldown
- `scripts/prevent_duplicate_instagram_publish.py`: 최근 Instagram caption 중복 검사

## 토큰 운영

- 모든 토큰은 GitHub Secrets로만 저장합니다.
- `.env`는 Git에서 제외됩니다.
- Meta, LinkedIn, X, Reddit 토큰의 만료·철회 여부는 실제 API 호출로 확인해야 합니다.
- GitHub Pages에 배포된 미디어는 공개 URL입니다.

## 공식 API 문서

- [Meta Instagram Content Publishing](https://developers.facebook.com/docs/instagram-platform/content-publishing/)
- [Meta Facebook Pages Posts](https://developers.facebook.com/docs/pages-api/posts/)
- [LinkedIn Posts API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api)
- [LinkedIn Images API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/images-api)
- [X Create Posts API](https://docs.x.com/x-api/posts/creation-of-a-post)
- [X Media Upload API](https://docs.x.com/x-api/media/upload-media)
