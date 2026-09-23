# GitHub Actions 게시 설정

이 저장소의 공식 실행 경로는 다음입니다.

```text
.github/workflows/daily-social-publish.yml
        ↓
scripts/generate_daily_content.py
scripts/build_instagram_reel.py
scripts/meta_publish.py
```

`social_publisher.py` 같은 별도 로컬 게시 CLI는 사용하지 않습니다.

## 필수 설정

Repository Settings에서 다음을 설정합니다.

1. Pages Source를 `GitHub Actions`로 설정
2. 아래 값을 Repository Secrets에 등록
3. `LINKEDIN_VERSION`과 `OPENAI_IMAGE_MODEL`은 필요하면 Variables로 등록

### Meta

```text
META_GRAPH_VERSION=v25.0
META_SYSTEM_USER_ACCESS_TOKEN=...
FACEBOOK_PAGE_ACCESS_TOKEN=...
FACEBOOK_PAGE_ID=...
INSTAGRAM_ACCOUNT_ID=...
```

Instagram은 Meta Business System User token을 사용합니다. Facebook은 Page access token을 별도로 사용합니다.

### LinkedIn

```text
LINKEDIN_ACCESS_TOKEN=...
LINKEDIN_AUTHOR_URN=urn:li:person:...
LINKEDIN_VERSION=202605
```

회원 게시에는 `w_member_social`, 조직 게시에는 `w_organization_social`과 조직 관리자 권한이 필요합니다.

### X

예약 게시에는 OAuth 1.0a Read and Write 값을 우선 사용합니다.

```text
X_API_KEY=...
X_API_KEY_SECRET=...
X_OAUTH1_ACCESS_TOKEN=...
X_OAUTH1_ACCESS_TOKEN_SECRET=...
```

OAuth 2.0 fallback을 사용할 경우 다음 값이 필요합니다.

```text
X_ACCESS_TOKEN=...
```

### Reddit

```text
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_USERNAME=...
REDDIT_PASSWORD=...
REDDIT_SUBREDDIT=...
REDDIT_FLAIR_ID=...
REDDIT_USER_AGENT=...
```

현재 Reddit 구현은 native gallery가 아니라 GitHub Pages의 이미지 URL을 포함한 self post입니다.

### 이미지 소싱

```text
PEXELS_API_KEY=...
PIXABAY_API_KEY=...
OPENAI_API_KEY=...
```

OpenAI 이미지 생성은 Pexels·Pixabay 결과가 최소 이미지 수를 채우지 못할 때만 사용됩니다.

## 예약 및 수동 실행

워크플로는 매일 09:00 KST에 실행됩니다.

수동 실행 입력값:

- `dry_run=true`: 생성, Pages 배포, URL·정책 검증만 수행
- `publish_scope=all`: 모든 채널 실행
- `publish_scope=instagram`: Instagram 캐러셀만 실행
- `publish_scope=instagram_reel`: Instagram Reel만 실행
- `publish_scope=facebook`: Facebook Page 실행
- `publish_scope=linkedin`: 한국어 LinkedIn 실행
- `publish_scope=linkedin_en`: 영어 LinkedIn 실행
- `publish_scope=x`: X API 실행
- `publish_scope=reddit`: Reddit 실행

## 실행 순서

1. Python 3.12와 의존성 설치
2. 현재 주제의 이미지 소싱
3. 날짜 기반 콘텐츠 패키지 생성
4. 게시 정책 검증
5. X 브라우저 handoff HTML 생성
6. Instagram Reel 생성
7. GitHub Pages에 PNG, JPG, MP4, handoff HTML 배포
8. 공개 미디어 URL과 Content-Type 검증
9. Instagram cooldown 확인
10. Instagram 최근 캡션 중복 확인
11. `scripts/meta_publish.py`로 채널별 게시
12. 채널별 결과 JSON을 artifact로 저장

## 채널별 실제 동작

- Instagram 캐러셀: 5장의 JPG를 Graph API carousel container로 게시
- Instagram Reel: 5장의 PNG를 세로형 MP4로 만든 뒤 Graph API로 게시
- Facebook: 5장의 PNG를 Page 다중 이미지 게시물로 게시
- LinkedIn: 5장의 PNG를 Images API에 업로드한 뒤 `multiImage` 게시물로 게시
- X: `x-mode.txt`에 따라 텍스트, 첫 이미지, 또는 Thread 게시
- Reddit: 제목과 본문에 Pages 이미지 URL을 포함한 self post

LinkedIn은 첫 슬라이드만 게시하지 않습니다. 현재 구현은 5장 전체를 게시합니다.

X handoff는 자동 fallback이 아닙니다. 모든 실행에서 생성되는 검토용 보조 산출물이며, X API를 사용할 수 없을 때 수동 브라우저 게시에 사용합니다.

## 이미지 품질과 정책 검증

`sync_topic_image_assets.py`는 주제별로 다음 순서를 사용합니다.

1. Pexels
2. Pixabay
3. OpenAI Image API

현재 주제는 최소 5개의 고유 이미지가 필요합니다. 생성기는 `visual-source-manifest.json`에 provider와 SHA-256을 기록하고, `validate_publish_policy.py`가 다음을 검사합니다.

- manifest 존재 여부
- 최소 고유 이미지 수
- provider가 Pexels, Pixabay, OpenAI 중 하나인지
- Instagram caption 첫 줄이 질문형인지
- Instagram caption에 해시태그가 5개 이상인지
- 비활성화된 pillar인지 여부

## 실패 처리

`meta_publish.py`는 채널별 오류를 결과 JSON에 기록할 수 있습니다. workflow의 일부 게시 단계는 `continue-on-error`와 `--allow-failures`를 사용하므로, GitHub Actions가 성공해도 artifact의 채널별 결과를 확인해야 합니다.

Instagram 중복 preflight API가 일시적으로 실패하면 현재 구현은 게시를 계속하고 `check_status=unavailable` 경고를 남깁니다.

## 공개 자산과 보안

GitHub Pages에 배포된 이미지와 영상은 공개 URL입니다. Instagram API가 공개 이미지 URL을 요구하기 때문에 필요한 설계입니다.

토큰은 반드시 GitHub Secrets에 저장하고, `.env`나 소스 파일에 커밋하지 않습니다. `pages-history` 브랜치는 과거 public asset을 보존하므로 저장소 크기와 보존 정책을 주기적으로 검토해야 합니다.
