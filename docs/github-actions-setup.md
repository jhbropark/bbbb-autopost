# GitHub Actions Social Publishing Setup

This repo can publish generated bbbb.beauty content without browser login by using:

1. Meta Business System User Token for Instagram
2. Facebook Page Access Token for Facebook Page publishing
3. LinkedIn OAuth access token for LinkedIn publishing
4. X OAuth 2.0 user access token for X publishing
5. GitHub Pages as public image hosting
6. GitHub Actions scheduled workflow

## Required GitHub Settings

1. Create or connect a GitHub repository.
2. Push this project to the repository.
3. In the repository, go to `Settings > Pages`.
4. Set source to `GitHub Actions`.
5. Add these repository secrets:

```text
META_GRAPH_VERSION=v25.0
META_SYSTEM_USER_ACCESS_TOKEN=...
FACEBOOK_PAGE_ACCESS_TOKEN=...
FACEBOOK_PAGE_ID=1195784186945659
INSTAGRAM_ACCOUNT_ID=17841424189525618
LINKEDIN_ACCESS_TOKEN=...
LINKEDIN_AUTHOR_URN=urn:li:person:...
LINKEDIN_VERSION=202605
X_API_KEY=...
X_API_KEY_SECRET=...
X_OAUTH1_ACCESS_TOKEN=...
X_OAUTH1_ACCESS_TOKEN_SECRET=...
X_ACCESS_TOKEN=...
X_REFRESH_TOKEN=...
X_CLIENT_ID=...
X_CLIENT_SECRET=...
```

Do not store these values in committed files.

## Meta Token Requirement

Use separate tokens for each publishing surface:

- Instagram: Meta Business system user token stored as `META_SYSTEM_USER_ACCESS_TOKEN`
- Facebook: Page access token stored as `FACEBOOK_PAGE_ACCESS_TOKEN`

Minimum Instagram system user token permissions:

```text
instagram_basic
instagram_content_publish
business_management
```

Minimum Facebook Page token permissions:

```text
pages_show_list
pages_read_engagement
pages_manage_posts
```

The Meta Business system user must have access to:

- Instagram account: `bbbb.beauty_official`

The Facebook Page access token must belong to:

- Facebook Page: `Beyond Beauty Building Brands`

Minimum LinkedIn token permissions:

```text
w_member_social
```

For an organization page, use `w_organization_social` and set `LINKEDIN_AUTHOR_URN` to
`urn:li:organization:{id}`. For a personal profile, use `urn:li:person:{id}`.

Recommended X credentials for scheduled publishing:

```text
X_API_KEY
X_API_KEY_SECRET
X_OAUTH1_ACCESS_TOKEN
X_OAUTH1_ACCESS_TOKEN_SECRET
```

Use OAuth 1.0a tokens with Read and Write permission for durable scheduled posting.
OAuth 2.0 access tokens expire, so they are only a fallback unless refresh handling is
managed separately.

Minimum X OAuth 2.0 user token scopes, if OAuth 2.0 is used:

```text
tweet.read
tweet.write
users.read
media.write
offline.access
```

Use an X user-context OAuth 2.0 token. App-only bearer tokens cannot create Posts.

## What The Workflow Does

`.github/workflows/daily-social-publish.yml` runs daily at `09:00 KST`.

Steps:

1. Generate the carousel images.
2. Copy images to a GitHub Pages artifact path.
3. Deploy the artifact to GitHub Pages.
4. Use the public Pages URLs as Instagram `image_url` values.
5. Publish an Instagram carousel.
6. Publish a Facebook multi-photo post.
7. Publish a LinkedIn image post using the first carousel slide.
8. Publish an X image post using the first carousel slide.
9. Upload a publish result JSON as a workflow artifact.

## Dry Run

Run the workflow manually with:

```text
dry_run = true
```

This validates generated image URLs and captions without publishing to Meta.

## Current Limitation

The current content generator is the MOA carousel generator:

```text
create_2026_06_16_moa_post.py
```

For a fully rotating daily calendar, add a date-based content router that selects the topic and generator for each day.
