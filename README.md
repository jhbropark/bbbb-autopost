# Social Publisher

브라우저에 매번 로그인하지 않고 공식 API로 Facebook 페이지, Instagram
프로페셔널 계정, LinkedIn 회원 또는 조직에 게시하는 로컬 CLI입니다.

## 지원 범위

- Facebook 페이지: 텍스트, 로컬 이미지 또는 공개 이미지 URL
- Instagram 비즈니스/크리에이터 계정: 공개 HTTPS 이미지 URL과 캡션
- LinkedIn 회원/조직: 텍스트와 로컬 이미지
- X 계정: 텍스트와 로컬 이미지

개인 Facebook 프로필 및 일반 Instagram 개인 계정은 공식 게시 API 대상이
아닙니다.

## 최초 설정

1. `.env.example`을 `.env`로 복사합니다.
2. Meta 개발자 앱에서 필요한 권한을 승인받고 사용자 액세스 토큰을
   `META_USER_ACCESS_TOKEN`에 입력합니다.
3. 채널을 조회합니다.

```powershell
Copy-Item .env.example .env
python .\social_publisher.py discover --platform meta
```

조회 결과의 Facebook 페이지 ID, 페이지 토큰, 연결된 Instagram 계정 ID를
`.env`에 넣습니다. Instagram 토큰에는 연결된 Facebook 페이지 액세스 토큰을
사용할 수 있습니다.

LinkedIn 개발자 앱에는 게시 대상에 따라 다음 권한이 필요합니다.

- 회원 게시: `w_member_social`
- 조직 게시: `w_organization_social` 및 해당 조직 관리자 권한

`LINKEDIN_AUTHOR_URN`은 `urn:li:person:{id}` 또는
`urn:li:organization:{id}` 형식입니다.

회원 토큰에 LinkedIn 프로필 조회 권한이 있으면 다음 명령으로 회원 URN을
조회할 수 있습니다.

```powershell
python .\social_publisher.py discover --platform linkedin
```

X 개발자 포털에서는 예약 게시 안정성을 위해 OAuth 1.0a Read and Write 토큰을
우선 사용합니다. 다음 값을 `.env`에 입력합니다.

```text
X_API_KEY=
X_API_KEY_SECRET=
X_OAUTH1_ACCESS_TOKEN=
X_OAUTH1_ACCESS_TOKEN_SECRET=
```

OAuth 2.0을 사용할 경우 최소 권한은 `tweet.read`, `tweet.write`, `users.read`,
`media.write`, `offline.access`입니다. 이 경우 `X_ACCESS_TOKEN`과
`X_REFRESH_TOKEN`도 관리해야 합니다.

```powershell
python .\social_publisher.py discover --platform x
```

## 설정 점검

```powershell
python .\social_publisher.py doctor
```

## 드라이런

```powershell
python .\social_publisher.py publish `
  --channels facebook,instagram,linkedin,x `
  --text "게시 테스트" `
  --image ".\artifacts\automation-3-2026-06-14-media-art.png" `
  --image-url "https://example.com/automation-3-2026-06-14-media-art.png" `
  --dry-run
```

## 실제 게시

`--dry-run`만 제거합니다.

```powershell
python .\social_publisher.py publish `
  --channels facebook,instagram,linkedin,x `
  --text-file ".\post.txt" `
  --image ".\artifacts\automation-3-2026-06-14-media-art.png" `
  --image-url "https://example.com/automation-3-2026-06-14-media-art.png"
```

Instagram Graph API는 Meta 서버가 가져갈 수 있는 공개 HTTPS 이미지 URL을
요구합니다. 로컬 파일만 있을 경우 S3, Cloudflare R2, Azure Blob Storage 등
공개 또는 서명 URL을 제공하는 저장소가 별도로 필요합니다.

## 토큰 운영

- `.env`는 Git에서 제외되며 외부에 공유하면 안 됩니다.
- Meta 및 LinkedIn 토큰은 만료되거나 철회될 수 있습니다.
- LinkedIn 일반 액세스 토큰은 보통 60일입니다. 프로그램 방식 갱신 토큰은
  해당 기능이 승인된 앱에서만 사용할 수 있습니다.
- `doctor`는 설정 존재 여부를 점검합니다. 실제 권한과 만료 여부는
  `discover` 또는 게시 호출에서 플랫폼 응답으로 확인됩니다.

## 공식 문서

- Meta Instagram Content Publishing:
  https://developers.facebook.com/docs/instagram-platform/content-publishing/
- Meta Facebook Pages Posts:
  https://developers.facebook.com/docs/pages-api/posts/
- LinkedIn Posts API:
  https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api
- LinkedIn Images API:
  https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/images-api
- X Create Posts API:
  https://docs.x.com/x-api/posts/creation-of-a-post
- X Media Upload API:
  https://docs.x.com/x-api/media/upload-media
