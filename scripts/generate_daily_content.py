#!/usr/bin/env python3
"""Generate a date-specific bbbb.beauty social package for the daily workflow."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
import json
import os
from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
ANCHOR_DATE = date(2026, 6, 22)

NAVY = "#1E293B"
WHITE = "#FFFFFF"
AQUA = "#0EA5E9"
HIGHLIGHT = AQUA
SOFT = "#F8F6F2"

WIDTH = 1080
HEIGHT = 1080
SAFE_X = 112
SAFE_RIGHT = 968
PHOTO_ROOT = ROOT / "assets" / "photo-backgrounds"

PHOTO_BACKGROUNDS = {
    "kbeauty-ma-system-risk": (
        PHOTO_ROOT / "kbeauty-ma" / "01-glass-building.jpg",
        PHOTO_ROOT / "kbeauty-ma" / "02-korean-cosmetics.jpg",
    ),
    "derma-cosmetic-expansion": (
        PHOTO_ROOT / "derma-bio" / "01-cosmetic-jar.jpg",
        PHOTO_ROOT / "derma-bio" / "02-lab-glassware.jpg",
    ),
}


@dataclass(frozen=True)
class Source:
    title: str
    url: str
    date: str
    note: str


@dataclass(frozen=True)
class Topic:
    slug: str
    pillar: str
    label: str
    hook: str
    one_liner: str
    evidence: tuple[tuple[str, str], ...]
    dilemma: tuple[tuple[str, str], ...]
    production: tuple[str, ...]
    checklist: tuple[str, ...]
    instagram: str
    facebook: str
    linkedin: str
    x_post: str
    sources: tuple[Source, ...]


HANKYUNG_KBEAUTY_MNA = Source(
    "국민 아이크림 아니었나…몸값 3조 잘 나가던 회사 결국",
    "https://www.hankyung.com/article/2026062336511",
    "2026-06-23",
    "AHC, 닥터자르트, 3CE 등 글로벌 인수 이후 성과 부진과 채널 리스크를 다룬 기사",
)
HANKYUNG_DRG = Source(
    "고은이 기자 페이지: 로레알·에스티로더 K뷰티 인수 사례",
    "https://www.hankyung.com/reporter/409?page=1",
    "2026",
    "닥터지, 닥터자르트, AHC, 3CE 등 K뷰티 M&A 관련 보도 묶음",
)
HANKYUNG_FOUNDERZ = Source(
    "아누아 업체 더파운더즈, 필러社 셀락바이오와 합작",
    "https://www.hankyung.com/article/2026040624461",
    "2026-04-06",
    "성분·가성비, 글로벌 확장, 미용기기·기능성 화장품 포트폴리오 트렌드",
)
HANKYUNG_BIO = Source(
    "K바이오 기술수출, 벌써 10조원 넘었다",
    "https://www.hankyung.com/article/2025061062231",
    "2025-06-10",
    "제약·바이오 기술 수출과 글로벌 기업의 K바이오 평가 흐름",
)


TOPICS = (
    Topic(
        "kbeauty-ma-system-risk",
        "K-Beauty M&A Signal",
        "MARKET SIGNAL",
        "글로벌 인수는\n브랜드의 끝이 아니라\n운영 시스템의 시험입니다.",
        "K뷰티 M&A 사례는 좋은 제품보다 더 중요한 것이 출시 속도, 채널 회복력, 현지 실행 시스템이라는 점을 보여줍니다.",
        (
            ("AHC", "2017년 유니레버 인수 후 매출 감소 흐름"),
            ("닥터자르트", "에스티로더 인수 후 영업손실 보도"),
            ("3CE", "로레알 편입 후 사업 구조 재정비"),
            ("닥터지", "로레알 인수 후 운영 리더십 교체"),
        ),
        (
            ("속도", "K뷰티는 트렌드 반응이 빠르지만 글로벌 의사결정은 느릴 수 있습니다."),
            ("채널", "중국·면세 의존은 성장도 빠르지만 충격도 크게 만듭니다."),
        ),
        (
            "제품 강점은 한 문장으로 압축합니다.",
            "근거는 성분, 사용 장면, 시장 맥락으로 분리합니다.",
            "채널별 콘텐츠는 같은 메시지를 다른 역할로 번역합니다.",
        ),
        (
            "핵심 제품 가설",
            "검증된 근거",
            "시장 리스크",
            "현지 실행 장면",
            "채널별 메시지",
        ),
        "K뷰티 M&A 사례가 보여주는 것은 제품력만으로는 충분하지 않다는 점입니다. 브랜드는 근거, 속도, 채널 실행을 하나의 시스템으로 설명해야 합니다.",
        "글로벌 기업이 인수한 K뷰티 브랜드의 성과 부진 사례는 콘텐츠 전략에도 같은 질문을 남깁니다. 좋은 제품을 어떻게 검증하고, 어떤 채널에서, 어떤 속도로 이해시키는가가 브랜드의 회복력을 결정합니다.",
        "문제:\nK뷰티 브랜드는 빠르게 성장하지만 글로벌 시스템 안에서는 속도와 실행력이 약해질 수 있습니다.\n\n해결:\n제품 메시지를 가설, 근거, 시장 리스크, 실행 장면으로 나눠 설계합니다.\n\n실행:\n1. 핵심 제품 가설을 한 문장으로 정리\n2. 성분·기전·사용 장면 근거를 분리\n3. 채널 의존 리스크를 콘텐츠에 반영\n4. Instagram은 훅, Facebook은 맥락, LinkedIn은 실행 프레임으로 운영",
        "K뷰티 M&A 사례가 말하는 것: 좋은 브랜드는 제품보다 실행 시스템으로 증명됩니다.",
        (HANKYUNG_KBEAUTY_MNA, HANKYUNG_DRG),
    ),
    Topic(
        "derma-cosmetic-expansion",
        "Derma Cosmetic Expansion",
        "DERMA + BIO",
        "더마코스메틱은\n성분을 파는 것이 아니라\n검증 가능한 사용 이유를 팝니다.",
        "성분·가성비 기반 K뷰티 성장과 바이오·미용기기 포트폴리오 확장은 콘텐츠에도 검증 구조를 요구합니다.",
        (
            ("성분", "아누아 등 성분·가성비 기반 글로벌 성장 흐름"),
            ("포트폴리오", "미용기기, 기능성 화장품, 건기식 결합 확대"),
            ("바이오", "제약·바이오 기술 수출과 글로벌 평가 강화"),
        ),
        (
            ("검증", "효능을 단정하지 않고 이해 가능한 근거로 전환해야 합니다."),
            ("확장", "제품군이 넓어질수록 브랜드 메시지는 더 단순해야 합니다."),
        ),
        (
            "성분을 기능이 아니라 사용 이유로 번역합니다.",
            "기전은 한 단계씩 시각화합니다.",
            "전후 맥락은 임상 표현이 아니라 소비자 이해로 정리합니다.",
        ),
        (
            "성분 메시지",
            "기전 장면",
            "사용 상황",
            "규제 표현 범위",
            "반복 가능한 포맷",
        ),
        "더마코스메틱 콘텐츠는 성분명을 나열하는 방식으로는 부족합니다. 고객이 왜 써야 하는지, 어떤 장면에서 이해해야 하는지까지 구조화해야 합니다.",
        "성분·가성비 기반 K뷰티와 바이오 기술 수출 흐름은 같은 메시지를 줍니다. 근거는 많을수록 좋은 것이 아니라, 사용자가 이해할 순서로 재배열될 때 신뢰가 됩니다.",
        "문제:\n성분, 기전, 기능성 메시지가 많아질수록 고객은 무엇을 믿어야 하는지 놓치기 쉽습니다.\n\n해결:\n성분 메시지, 작용 장면, 사용 상황, 표현 범위를 분리합니다.\n\n실행:\nInstagram은 사용 이유를 한 장면으로 보여주고, LinkedIn은 제작 기준과 검증 프로세스를 설명합니다.",
        "더마코스메틱의 핵심은 성분보다 사용자가 이해할 수 있는 근거 구조입니다.",
        (HANKYUNG_FOUNDERZ, HANKYUNG_BIO),
    ),
)


INSTAGRAM_DAILY_ANGLES = (
    "Today lens: market signal -> content decision.",
    "Today lens: evidence -> customer understanding.",
    "Today lens: channel risk -> message structure.",
    "Today lens: execution system -> repeatable publishing.",
)


def font_path(bold: bool) -> Path:
    candidates = [
        os.getenv("FONT_BOLD" if bold else "FONT_REGULAR", ""),
        r"C:\Windows\Fonts\malgunbd.ttf" if bold else r"C:\Windows\Fonts\malgun.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc" if bold else "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return Path(candidate)
    raise FileNotFoundError("No Korean font found.")


REGULAR = font_path(False)
BOLD = font_path(True)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(BOLD if bold else REGULAR), size)


def wrap(value: str, width: int) -> str:
    return "\n".join(textwrap.wrap(" ".join(value.split()), width=width, break_long_words=False))


def draw_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    value: str,
    size: int,
    fill: str | tuple[int, int, int, int],
    bold: bool = False,
    spacing: int = 8,
    anchor: str | None = None,
) -> None:
    draw.multiline_text(xy, value, font=font(size, bold), fill=fill, spacing=spacing, anchor=anchor)


def fit_text(draw: ImageDraw.ImageDraw, value: str, max_width: int, start_size: int, min_size: int) -> int:
    for size in range(start_size, min_size - 1, -2):
        box = draw.multiline_textbbox((0, 0), value, font=font(size, True), spacing=8)
        if box[2] - box[0] <= max_width:
            return size
    return min_size


def fallback_background() -> Image.Image:
    photo = Image.new("RGBA", (WIDTH, HEIGHT), (30, 40, 48, 255))
    draw = ImageDraw.Draw(photo)
    for y in range(HEIGHT):
        ratio = y / (HEIGHT - 1)
        r = int(164 * (1 - ratio) + 18 * ratio)
        g = int(187 * (1 - ratio) + 24 * ratio)
        b = int(190 * (1 - ratio) + 32 * ratio)
        draw.line((0, y, WIDTH, y), fill=(r, g, b, 255))
    return photo


def load_topic_photo(topic: Topic, page: int) -> Image.Image:
    candidates = [path for path in PHOTO_BACKGROUNDS.get(topic.slug, ()) if path.is_file()]
    if not candidates:
        return fallback_background()

    source = candidates[(page - 1) % len(candidates)]
    photo = Image.open(source)
    photo = ImageOps.exif_transpose(photo).convert("RGB")
    photo = ImageOps.fit(photo, (WIDTH, HEIGHT), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    photo = ImageEnhance.Color(photo).enhance(0.72)
    photo = ImageEnhance.Contrast(photo).enhance(1.08)
    return photo.convert("RGBA")


def add_photo_background(image: Image.Image, topic: Topic, page: int) -> None:
    photo = load_topic_photo(topic, page)
    photo = photo.filter(ImageFilter.GaussianBlur(1.2))

    noise = Image.effect_noise((WIDTH, HEIGHT), 20).convert("L")
    noise = ImageOps.colorize(noise, (0, 0, 0), (255, 255, 255)).convert("RGBA")
    noise.putalpha(18)
    photo = Image.alpha_composite(photo, noise)

    shade = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shade_draw = ImageDraw.Draw(shade)
    for y in range(HEIGHT):
        alpha = int(70 + 145 * (y / HEIGHT) ** 1.05)
        shade_draw.line((0, y, WIDTH, y), fill=(30, 41, 59, alpha))
    for x in range(WIDTH):
        alpha = int(165 * (1 - min(1, x / 760)))
        shade_draw.line((x, 0, x, HEIGHT), fill=(10, 16, 27, alpha))

    image.alpha_composite(photo)
    image.alpha_composite(shade)


def header(draw: ImageDraw.ImageDraw, topic: Topic, page: int, section: str) -> None:
    draw_text(draw, (SAFE_X, 68), f"bbbb / {topic.pillar.upper()}", 18, WHITE, True)
    draw_text(draw, (SAFE_RIGHT, 68), f"{page:02d}/05", 18, AQUA, True, anchor="ra")
    draw.rounded_rectangle((SAFE_X, 132, SAFE_X + 340, 178), radius=23, fill=(0, 0, 0, 210))
    draw_text(draw, (SAFE_X + 24, 144), section, 16, WHITE, True)


def footer(draw: ImageDraw.ImageDraw) -> None:
    draw_text(draw, (SAFE_X, 1010), "BBBB BEAUTY INTELLIGENCE", 14, (255, 255, 255, 215), True)


def title(draw: ImageDraw.ImageDraw, y: int, value: str, size: int = 55) -> None:
    size = fit_text(draw, value, SAFE_RIGHT - SAFE_X, size, 38)
    draw_text(draw, (SAFE_X + 3, y + 3), value, size, (0, 0, 0, 125), True, 9)
    draw_text(draw, (SAFE_X, y), value, size, WHITE, True, 9)


def label_bar(draw: ImageDraw.ImageDraw, y: int, label: str, fill: str = HIGHLIGHT) -> None:
    draw.rectangle((SAFE_X, y, SAFE_RIGHT, y + 60), fill=fill)
    draw_text(draw, ((SAFE_X + SAFE_RIGHT) // 2, y + 13), label, 27, WHITE, True, anchor="ma")


def slide_hook(topic: Topic) -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    add_photo_background(image, topic, 1)
    draw = ImageDraw.Draw(image)
    header(draw, topic, 1, topic.label)
    title(draw, 310, topic.hook, 60)
    draw_text(draw, (SAFE_X, 720), wrap(topic.one_liner, 28), 30, (255, 255, 255, 235), False, 10)
    footer(draw)
    return image.convert("RGB")


def slide_evidence(topic: Topic) -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    add_photo_background(image, topic, 2)
    draw = ImageDraw.Draw(image)
    header(draw, topic, 2, "ARTICLE FACTS")
    title(draw, 202, "기사에서 뽑은\n시장 신호", 52)
    y = 425
    for name, fact in topic.evidence:
        draw.rectangle((SAFE_X, y, SAFE_X + 222, y + 72), fill=(14, 165, 233, 222))
        draw.rectangle((SAFE_X + 244, y, SAFE_RIGHT, y + 72), fill=(255, 255, 255, 214))
        draw_text(draw, (SAFE_X + 111, y + 18), name, 25, WHITE, True, anchor="ma")
        draw_text(draw, (SAFE_X + 270, y + 18), fact, 24, "#111111", False)
        y += 104
    footer(draw)
    return image.convert("RGB")


def slide_dilemma(topic: Topic) -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    add_photo_background(image, topic, 3)
    draw = ImageDraw.Draw(image)
    header(draw, topic, 3, "DILEMMA")
    title(draw, 195, "브랜드가 겪는\n두 가지 딜레마", 55)
    y = 430
    for idx, (label, detail) in enumerate(topic.dilemma, start=1):
        label_bar(draw, y, f"{idx}. {label}", HIGHLIGHT)
        draw_text(draw, (SAFE_X, y + 92), wrap(detail, 26), 30, (255, 255, 255, 235), False, 10)
        draw_text(draw, ((SAFE_X + SAFE_RIGHT) // 2, y + 172), "↓", 46, HIGHLIGHT, True, anchor="ma")
        y += 255
    footer(draw)
    return image.convert("RGB")


def slide_production(topic: Topic) -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    add_photo_background(image, topic, 4)
    draw = ImageDraw.Draw(image)
    header(draw, topic, 4, "CONTENT SYSTEM")
    title(draw, 190, "게시물은\n이렇게 바꿔야 합니다", 54)
    y = 430
    for idx, item in enumerate(topic.production, start=1):
        draw.rounded_rectangle((SAFE_X, y, SAFE_RIGHT, y + 88), radius=12, fill=(255, 255, 255, 210))
        draw_text(draw, (SAFE_X + 28, y + 23), f"{idx:02d}", 26, AQUA, True)
        draw_text(draw, (SAFE_X + 112, y + 24), item, 27, "#111111", True)
        y += 116
    footer(draw)
    return image.convert("RGB")


def slide_checklist(topic: Topic) -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    add_photo_background(image, topic, 5)
    draw = ImageDraw.Draw(image)
    header(draw, topic, 5, "SAVE THIS")
    title(draw, 188, f"{topic.pillar}\n체크리스트", 50)
    y = 425
    for idx, item in enumerate(topic.checklist, start=1):
        draw.rectangle((SAFE_X, y, SAFE_X + 70, y + 58), fill=HIGHLIGHT)
        draw_text(draw, (SAFE_X + 35, y + 13), str(idx), 25, WHITE, True, anchor="ma")
        draw_text(draw, (SAFE_X + 96, y + 11), item, 30, WHITE, True)
        y += 86
    footer(draw)
    return image.convert("RGB")


def instagram_caption_for(topic: Topic, target_date: date) -> str:
    cycle = ((target_date - ANCHOR_DATE).days // max(1, len(TOPICS))) % len(INSTAGRAM_DAILY_ANGLES)
    return f"{topic.instagram}\n\n{INSTAGRAM_DAILY_ANGLES[cycle]} #{target_date.isoformat()}"


def create_package(target_date: date, out_root: Path) -> Path:
    index = (target_date - ANCHOR_DATE).days % len(TOPICS)
    topic = TOPICS[index]
    out = out_root / f"{target_date.isoformat()}-{topic.slug}"
    carousel = out / "carousel"
    carousel.mkdir(parents=True, exist_ok=True)

    slides = [
        slide_hook(topic),
        slide_evidence(topic),
        slide_dilemma(topic),
        slide_production(topic),
        slide_checklist(topic),
    ]
    for page, image in enumerate(slides, start=1):
        image.save(carousel / f"{page:02d}.png", quality=95)

    source_lines = "\n".join(f"- {source.title} ({source.date}) {source.url}" for source in topic.sources)
    (out / "instagram-caption.txt").write_text(instagram_caption_for(topic, target_date), encoding="utf-8")
    (out / "facebook-caption.txt").write_text(f"{topic.facebook}\n\n참고: 한국경제 기사 기반 시장 신호 분석", encoding="utf-8")
    (out / "linkedin-post.txt").write_text(f"{topic.linkedin}\n\n참고 기사:\n{source_lines}", encoding="utf-8")
    (out / "reddit-title.txt").write_text(topic.x_post, encoding="utf-8")
    (out / "reddit-post.txt").write_text(
        f"{topic.linkedin}\n\n참고 기사:\n{source_lines}",
        encoding="utf-8",
    )
    (out / "x-post.txt").write_text(topic.x_post, encoding="utf-8")
    (out / "x-thread.txt").write_text("\n---\n".join((topic.x_post, topic.hook, *topic.checklist[:3])), encoding="utf-8")
    (out / "x-mode.txt").write_text(("short", "image", "thread", "short", "image")[target_date.toordinal() % 5], encoding="utf-8")
    (out / "sources.json").write_text(
        json.dumps([source.__dict__ for source in topic.sources], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out / "README.md").write_text(
        f"# {target_date.isoformat()} Daily Content\n\n- Pillar: {topic.pillar}\n- Source: Hankyung market signal\n- Format: 5-slide structured carousel\n\n{source_lines}\n",
        encoding="utf-8",
    )
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--out-root", type=Path, default=ROOT / "artifacts")
    args = parser.parse_args()
    target_date = date.fromisoformat(args.date)
    out = create_package(target_date, args.out_root)
    print(out.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
