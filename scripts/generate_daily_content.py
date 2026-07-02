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
SOFT = "#F8F6F2"
INK = "#111827"

WIDTH = 1080
HEIGHT = 1080
SAFE_X = 104
SAFE_RIGHT = 976
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
    "clinical-proof-translation": (
        PHOTO_ROOT / "derma-bio" / "02-lab-glassware.jpg",
        PHOTO_ROOT / "derma-bio" / "01-cosmetic-jar.jpg",
    ),
    "post-acquisition-brand-system": (
        PHOTO_ROOT / "kbeauty-ma" / "01-glass-building.jpg",
        PHOTO_ROOT / "kbeauty-ma" / "02-korean-cosmetics.jpg",
    ),
}

PAGE_VARIANTS = (
    {"photo": 0, "center": (0.38, 0.45), "zoom": 1.00, "blur": 0.8, "mirror": False, "tint": (5, 14, 24)},
    {"photo": 1, "center": (0.55, 0.52), "zoom": 1.08, "blur": 0.5, "mirror": False, "tint": (10, 20, 28)},
    {"photo": 0, "center": (0.68, 0.42), "zoom": 1.22, "blur": 1.1, "mirror": True, "tint": (9, 22, 32)},
    {"photo": 1, "center": (0.32, 0.60), "zoom": 1.18, "blur": 0.8, "mirror": True, "tint": (15, 22, 32)},
    {"photo": 0, "center": (0.50, 0.64), "zoom": 1.35, "blur": 1.4, "mirror": False, "tint": (6, 20, 31)},
)


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
    "한국경제 K뷰티 M&A 관련 보도",
    "https://www.hankyung.com/article/2026062336511",
    "2026-06-23",
    "글로벌 인수 이후 K뷰티 브랜드가 겪는 실적, 채널, 운영 이슈를 다룬 기사",
)
HANKYUNG_DRG = Source(
    "한국경제 K뷰티 M&A 보도 묶음",
    "https://www.hankyung.com/reporter/409?page=1",
    "2026",
    "AHC, 닥터자르트, 3CE 등 K뷰티 인수 이후의 브랜드 운영 리스크를 다룬 보도 묶음",
)
HANKYUNG_FOUNDERZ = Source(
    "한국경제 더파운더즈·스킨바이오 관련 보도",
    "https://www.hankyung.com/article/2026040624461",
    "2026-04-06",
    "성분, 가성비, 글로벌 확장, 미용기기·기능성 화장품 포트폴리오 확장 흐름",
)
HANKYUNG_BIO = Source(
    "한국경제 K바이오 기술수출 관련 보도",
    "https://www.hankyung.com/article/2025061062231",
    "2025-06-10",
    "제약·바이오 기술 수출과 글로벌 기업의 한국 바이오 평가 흐름",
)


TOPICS = (
    Topic(
        "kbeauty-ma-system-risk",
        "K-Beauty M&A Signal",
        "MARKET SIGNAL",
        "K뷰티 인수 후 더 중요해지는 것은\n제품력이 아니라 운영 시스템입니다.",
        "인수 후 성과가 흔들리는 브랜드는 제품이 부족해서만이 아니라 속도, 채널, 의사결정 구조가 달라졌기 때문입니다.",
        (
            ("브랜드", "AHC, 닥터자르트, 3CE 사례는 인수 이후 성과가 자동으로 보장되지 않음을 보여줍니다."),
            ("채널", "면세, 중국, 플랫폼 의존도가 높을수록 외부 변수에 브랜드가 크게 흔들립니다."),
            ("운영", "글로벌 본사의 승인 구조가 K뷰티 특유의 빠른 출시 속도와 충돌할 수 있습니다."),
        ),
        (
            ("속도", "K뷰티는 빠른 기획과 출시가 강점이지만, 인수 이후에는 의사결정 단계가 늘어납니다."),
            ("시스템", "브랜드 자율성을 남길지, 글로벌 시스템으로 통합할지에 따라 성과가 달라집니다."),
        ),
        (
            "제품 강점을 한 문장으로 압축합니다.",
            "성분·사용 장면·채널 리스크를 분리합니다.",
            "브랜드 메시지를 Instagram, Facebook, LinkedIn별 역할로 재배치합니다.",
        ),
        (
            "인수 후에도 유지해야 할 속도",
            "브랜드가 증명해야 할 제품 가설",
            "채널 의존도가 만드는 리스크",
            "글로벌 시스템 안에서 필요한 운영 언어",
            "콘텐츠가 설명해야 할 소비자 선택 이유",
        ),
        "K뷰티 M&A 사례가 말하는 핵심은 단순합니다. 제품력은 출발점이고, 성과는 운영 시스템에서 결정됩니다. 브랜드는 성분보다 먼저 ‘왜 지금 이 제품을 선택해야 하는가’를 증명해야 합니다.",
        "K뷰티 브랜드가 글로벌 기업에 인수된 뒤 더 어려워지는 지점은 제품 자체보다 운영 구조입니다.\n\n좋은 제품이 있어도 출시 속도, 채널 의존도, 본사 의사결정 구조가 맞지 않으면 브랜드의 장점은 빠르게 약해집니다.\n\nBBBB가 콘텐츠에서 먼저 보는 것은 세 가지입니다.\n1. 제품이 해결하는 문제가 한 문장으로 설명되는가\n2. 성분과 효능이 소비자 언어로 번역되는가\n3. 채널별 메시지가 같은 결론을 향해 움직이는가\n\nK뷰티 콘텐츠는 예쁜 비주얼보다 먼저 검증 가능한 브랜드 구조를 가져야 합니다.",
        "문제:\nK뷰티 브랜드는 빠르게 성장하지만, 인수 이후에는 글로벌 본사의 승인 구조와 기존 채널 의존도 안에서 속도를 잃을 수 있습니다.\n\n해결:\n브랜드 메시지를 제품력, 근거, 채널, 운영 구조로 분해해야 합니다. 그래야 콘텐츠가 단순 홍보가 아니라 브랜드의 선택 이유를 설명합니다.\n\n실행:\n1. 제품 가설을 한 문장으로 정의\n2. 성분·기전·사용 장면을 분리\n3. 채널별 콘텐츠 역할 설정\n4. Instagram은 직관, Facebook은 맥락, LinkedIn은 운영 프레임으로 설계",
        "K뷰티 M&A 사례가 주는 교훈: 제품력은 시작이고, 성과는 운영 시스템에서 결정됩니다.",
        (HANKYUNG_KBEAUTY_MNA, HANKYUNG_DRG),
    ),
    Topic(
        "derma-cosmetic-expansion",
        "Derma Cosmetic Expansion",
        "DERMA + BIO",
        "더마코스메틱은 성분을 파는 것이 아니라\n검증 가능한 사용 이유를 팝니다.",
        "성분·가성비 기반 K뷰티 성장과 바이오 기술 수출 흐름은 콘텐츠에 더 높은 수준의 근거 구조를 요구합니다.",
        (
            ("성분", "성분명만 제시하면 전문적으로 보이지만 소비자의 선택 이유로 바로 연결되지는 않습니다."),
            ("포트폴리오", "미용기기, 기능성 화장품, 건강 영역이 결합되며 설명 범위가 넓어졌습니다."),
            ("바이오", "제약·바이오 기술 수출 흐름은 효능 표현의 신뢰 기준을 높입니다."),
        ),
        (
            ("근거", "많이 말하는 것이 아니라 이해 가능한 순서로 배열해야 신뢰가 생깁니다."),
            ("확장", "제품군이 넓어질수록 브랜드 메시지는 더 단순하고 반복 가능해야 합니다."),
        ),
        (
            "성분을 기능이 아니라 사용 이유로 번역합니다.",
            "기전은 복잡한 설명이 아니라 3단계 흐름으로 시각화합니다.",
            "효능 표현은 소비자 언어와 규제 가능한 표현 범위를 함께 검토합니다.",
        ),
        (
            "핵심 성분의 역할",
            "작용 기전의 순서",
            "사용자가 느끼는 장면",
            "규제 리스크가 낮은 표현",
            "반복 가능한 설명 포맷",
        ),
        "더마코스메틱 콘텐츠는 성분명을 나열하는 방식으로는 부족합니다. 사용자가 이해할 수 있는 작용 순서, 선택 이유, 표현 범위까지 함께 설계해야 합니다.",
        "더마코스메틱 콘텐츠가 짧아 보이는 이유는 보통 정보가 부족해서가 아니라 구조가 없기 때문입니다.\n\n성분, 기전, 효능, 사용 장면을 한 번에 말하면 전문성이 아니라 복잡함이 됩니다. 반대로 같은 정보를 ‘문제-기전-사용 이유-선택 기준’으로 배열하면 브랜드의 신뢰도가 올라갑니다.\n\nBBBB는 더마·바이오 기반 콘텐츠를 만들 때 다음 순서를 씁니다.\n1. 성분이 아니라 고객의 불편에서 시작\n2. 작용 기전을 3단계로 정리\n3. 효능 표현은 과장보다 이해 가능성을 우선\n4. 마지막에는 구매 이유가 아니라 선택 기준을 남김\n\n전문성은 어려운 단어가 아니라 정확한 순서에서 나옵니다.",
        "문제:\n성분, 기전, 기능성 메시지가 많아질수록 고객은 무엇을 믿어야 하는지 놓치기 쉽습니다.\n\n해결:\n성분 메시지, 작용 기전, 사용 상황, 표현 범위를 분리합니다.\n\n실행:\nInstagram은 사용 이유를 한 장면으로 보여주고, Facebook은 왜 이 구조가 필요한지 설명하며, LinkedIn은 기획 기준과 검증 프로세스를 공유합니다.",
        "더마코스메틱의 전문성은 성분 수가 아니라 사용자가 이해할 수 있는 근거 구조에서 나옵니다.",
        (HANKYUNG_FOUNDERZ, HANKYUNG_BIO),
    ),
    Topic(
        "clinical-proof-translation",
        "Evidence Translation",
        "PROOF SYSTEM",
        "효능 콘텐츠는 ‘좋다’고 말하는 순간보다\n증거를 번역하는 순간에 신뢰가 생깁니다.",
        "뷰티·메디컬 콘텐츠의 핵심은 데이터 자체가 아니라 데이터를 고객의 판단 언어로 바꾸는 과정입니다.",
        (
            ("데이터", "성분, 시험, 논문, 사용 후기는 서로 다른 종류의 근거입니다."),
            ("언어", "전문 용어는 신뢰를 만들 수 있지만 이해를 막을 수도 있습니다."),
            ("판단", "고객은 효능보다 먼저 ‘내 상황에 맞는가’를 확인합니다."),
        ),
        (
            ("정확성", "표현을 줄이면 안전하지만 메시지가 약해질 수 있습니다."),
            ("이해도", "쉽게 풀면 전달력은 올라가지만 근거의 경계가 흐려질 수 있습니다."),
        ),
        (
            "근거 유형을 시험, 성분, 사용 경험으로 구분합니다.",
            "효능 표현을 가능한 범위와 피해야 할 범위로 나눕니다.",
            "고객이 판단할 수 있는 체크포인트를 남깁니다.",
        ),
        (
            "근거의 출처",
            "표현 가능한 효능 범위",
            "사용자가 확인할 장면",
            "과장으로 보일 수 있는 단어",
            "구매보다 먼저 필요한 판단 기준",
        ),
        "효능 콘텐츠는 더 강하게 말하는 것이 아니라 더 정확하게 이해시키는 일입니다. 고객이 판단할 수 있는 언어로 근거를 번역해야 합니다.",
        "뷰티·메디컬 콘텐츠에서 전문성은 주장 강도가 아니라 근거의 번역 방식으로 드러납니다.\n\n소비자는 ‘효과가 좋다’는 말을 듣고 움직이지 않습니다. 어떤 근거가 있고, 그 근거가 내 피부 상태나 사용 장면과 어떻게 연결되는지를 이해할 때 선택합니다.\n\n콘텐츠는 다음 네 가지를 구분해야 합니다.\n1. 실험이나 시험으로 확인된 사실\n2. 성분에서 추론 가능한 작용\n3. 사용자가 체감할 수 있는 장면\n4. 규제와 신뢰를 위해 피해야 할 표현\n\n좋은 콘텐츠는 제품을 과장하지 않고도 선택 이유를 선명하게 만듭니다.",
        "문제:\n뷰티 브랜드는 효능을 강하게 말하고 싶지만, 과장된 표현은 신뢰와 규제 리스크를 동시에 만듭니다.\n\n해결:\n근거를 주장으로 바로 바꾸지 않고, 근거 유형과 표현 범위를 먼저 정리합니다.\n\n실행:\n콘텐츠는 데이터, 해석, 고객 장면, 선택 기준을 분리해 설계해야 합니다. 이렇게 해야 전문성은 유지되고 고객 이해도는 높아집니다.",
        "좋은 효능 콘텐츠는 더 세게 말하지 않습니다. 근거를 고객의 판단 언어로 번역합니다.",
        (HANKYUNG_FOUNDERZ, HANKYUNG_BIO),
    ),
    Topic(
        "post-acquisition-brand-system",
        "Post-Acquisition Brand System",
        "OPERATING MODEL",
        "인수 이후 브랜드가 약해지는 이유는\n취향이 아니라 운영 언어가 바뀌기 때문입니다.",
        "K뷰티 브랜드가 글로벌 시스템 안에서 유지해야 할 것은 감각보다 더 명확한 의사결정 언어입니다.",
        (
            ("속도", "기획, 샘플, 출시의 리듬이 느려지면 트렌드 반응성이 떨어집니다."),
            ("자율성", "창업자 감각과 본사 기준 사이의 역할 정의가 필요합니다."),
            ("콘텐츠", "브랜드 언어가 약해지면 제품은 있어도 선택 이유가 흐려집니다."),
        ),
        (
            ("통합", "글로벌 시스템은 리스크를 줄이지만 브랜드 고유의 감각을 희석할 수 있습니다."),
            ("자율", "자율성은 속도를 지키지만 관리 체계가 없으면 일관성이 약해질 수 있습니다."),
        ),
        (
            "브랜드가 유지해야 할 고유 언어를 정의합니다.",
            "본사가 관리해야 할 기준과 현장이 판단할 기준을 나눕니다.",
            "콘텐츠는 제품 설명이 아니라 운영 원칙의 외부 표현으로 설계합니다.",
        ),
        (
            "브랜드가 잃지 말아야 할 감각",
            "글로벌 시스템에서 필요한 기준",
            "현장이 빠르게 결정할 수 있는 범위",
            "소비자가 반복해서 이해할 메시지",
            "콘텐츠로 증명할 운영 원칙",
        ),
        "인수 이후 브랜드가 흔들리는 이유는 감각이 부족해서가 아닙니다. 의사결정 언어가 바뀌기 때문입니다. 콘텐츠는 그 변화를 고객이 이해할 수 있게 정리해야 합니다.",
        "인수 이후 K뷰티 브랜드가 어려워지는 이유는 단순히 트렌드가 바뀌어서가 아닙니다.\n\n브랜드가 빠르게 움직이던 방식, 창업자가 판단하던 기준, 현장에서 감각적으로 정리되던 언어가 글로벌 시스템 안에서 다른 규칙으로 바뀌기 때문입니다.\n\n이때 콘텐츠는 제품 홍보물이 아니라 운영 언어의 번역물이 되어야 합니다.\n1. 브랜드가 지켜야 할 고유한 감각\n2. 본사가 관리해야 할 리스크 기준\n3. 현장이 빠르게 판단할 수 있는 범위\n4. 고객에게 반복해서 전달할 선택 이유\n\n강한 브랜드는 예쁜 말보다 일관된 판단 구조를 먼저 가집니다.",
        "문제:\n인수 이후 브랜드는 더 큰 자원을 얻지만, 동시에 속도와 고유 언어를 잃을 수 있습니다.\n\n해결:\n콘텐츠를 단순 캠페인이 아니라 운영 원칙을 외부로 번역하는 시스템으로 설계해야 합니다.\n\n실행:\n브랜드 고유 언어, 본사 기준, 현장 판단 범위, 고객 선택 이유를 분리해 콘텐츠 구조에 반영합니다.",
        "인수 이후 브랜드의 경쟁력은 자본보다 운영 언어에서 갈립니다.",
        (HANKYUNG_KBEAUTY_MNA, HANKYUNG_DRG),
    ),
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


def text_height(value: str, size: int, bold: bool = False, spacing: int = 8) -> int:
    probe = Image.new("RGB", (10, 10))
    box = ImageDraw.Draw(probe).multiline_textbbox((0, 0), value, font=font(size, bold), spacing=spacing)
    return box[3] - box[1]


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
        r = int(178 * (1 - ratio) + 16 * ratio)
        g = int(190 * (1 - ratio) + 26 * ratio)
        b = int(192 * (1 - ratio) + 39 * ratio)
        draw.line((0, y, WIDTH, y), fill=(r, g, b, 255))
    return photo


def load_topic_photo(topic: Topic, page: int) -> Image.Image:
    candidates = [path for path in PHOTO_BACKGROUNDS.get(topic.slug, ()) if path.is_file()]
    if not candidates:
        return fallback_background()

    variant = PAGE_VARIANTS[(page - 1) % len(PAGE_VARIANTS)]
    source = candidates[int(variant["photo"]) % len(candidates)]
    photo = Image.open(source)
    photo = ImageOps.exif_transpose(photo).convert("RGB")
    photo = ImageOps.fit(
        photo,
        (round(WIDTH / float(variant["zoom"])), round(HEIGHT / float(variant["zoom"]))),
        method=Image.Resampling.LANCZOS,
        centering=variant["center"],
    )
    photo = photo.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    if variant["mirror"]:
        photo = ImageOps.mirror(photo)
    photo = ImageEnhance.Color(photo).enhance(0.68)
    photo = ImageEnhance.Contrast(photo).enhance(1.16)
    return photo.convert("RGBA").filter(ImageFilter.GaussianBlur(float(variant["blur"])))


def add_photo_background(image: Image.Image, topic: Topic, page: int) -> None:
    photo = load_topic_photo(topic, page)
    variant = PAGE_VARIANTS[(page - 1) % len(PAGE_VARIANTS)]
    tint = Image.new("RGBA", image.size, (*variant["tint"], 72))
    photo = Image.alpha_composite(photo, tint)

    shade = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shade_draw = ImageDraw.Draw(shade)
    for y in range(HEIGHT):
        alpha = int(42 + 160 * (y / HEIGHT) ** 1.1)
        shade_draw.line((0, y, WIDTH, y), fill=(30, 41, 59, alpha))
    for x in range(WIDTH):
        alpha = int(150 * (1 - min(1, x / 760)))
        shade_draw.line((x, 0, x, HEIGHT), fill=(10, 16, 27, alpha))

    image.alpha_composite(photo)
    image.alpha_composite(shade)


def header(draw: ImageDraw.ImageDraw, topic: Topic, page: int, section: str) -> None:
    draw.rounded_rectangle((SAFE_X, 58, SAFE_RIGHT, 112), radius=27, fill=(30, 41, 59, 230))
    draw_text(draw, (SAFE_X + 28, 74), f"bbbb / {topic.pillar.upper()}", 17, WHITE, True)
    draw_text(draw, (SAFE_RIGHT - 28, 74), f"{page:02d}/05", 17, AQUA, True, anchor="ra")
    draw.rounded_rectangle((SAFE_X, 150, SAFE_X + 360, 196), radius=23, fill=(0, 0, 0, 205))
    draw_text(draw, (SAFE_X + 24, 162), section, 15, WHITE, True)


def footer(draw: ImageDraw.ImageDraw) -> None:
    draw_text(draw, (SAFE_X, 1012), "BBBB BEAUTY INTELLIGENCE", 14, (255, 255, 255, 220), True)
    draw.rounded_rectangle((SAFE_RIGHT - 178, 996, SAFE_RIGHT, 1028), radius=16, fill=(30, 41, 59, 220))
    draw_text(draw, (SAFE_RIGHT - 89, 1005), "SAVE / SHARE", 13, WHITE, True, anchor="ma")


def title(draw: ImageDraw.ImageDraw, y: int, value: str, size: int = 54, color: str = WHITE) -> None:
    size = fit_text(draw, value, SAFE_RIGHT - SAFE_X, size, 36)
    draw_text(draw, (SAFE_X + 3, y + 3), value, size, (0, 0, 0, 145), True, 10)
    draw_text(draw, (SAFE_X, y), value, size, color, True, 10)


def translucent_panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], alpha: int = 205) -> None:
    draw.rounded_rectangle(box, radius=24, fill=(248, 246, 242, alpha))


def slide_hook(topic: Topic) -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    add_photo_background(image, topic, 1)
    draw = ImageDraw.Draw(image)
    header(draw, topic, 1, topic.label)
    title(draw, 305, topic.hook, 57)
    draw_text(draw, (SAFE_X, 720), wrap(topic.one_liner, 30), 29, (255, 255, 255, 238), False, 10)
    footer(draw)
    return image.convert("RGB")


def slide_evidence(topic: Topic) -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    add_photo_background(image, topic, 2)
    draw = ImageDraw.Draw(image)
    header(draw, topic, 2, "ARTICLE FACTS")
    title(draw, 206, "기사에서 읽어야 할\n세 가지 시장 신호", 51)
    y = 448
    for name, fact in topic.evidence:
        draw.rounded_rectangle((SAFE_X, y, SAFE_X + 188, y + 82), radius=8, fill=(14, 165, 233, 230))
        translucent_panel(draw, (SAFE_X + 210, y, SAFE_RIGHT, y + 82), 222)
        draw_text(draw, (SAFE_X + 94, y + 24), name, 23, WHITE, True, anchor="ma")
        draw_text(draw, (SAFE_X + 238, y + 18), wrap(fact, 30), 21, INK, False, 5)
        y += 110
    footer(draw)
    return image.convert("RGB")


def slide_dilemma(topic: Topic) -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    add_photo_background(image, topic, 3)
    draw = ImageDraw.Draw(image)
    header(draw, topic, 3, "DILEMMA")
    title(draw, 190, "브랜드가 겪는\n핵심 딜레마", 55)
    y = 420
    for idx, (label, detail) in enumerate(topic.dilemma, start=1):
        draw.rectangle((SAFE_X, y, SAFE_RIGHT, y + 58), fill=(14, 165, 233, 225))
        draw_text(draw, ((SAFE_X + SAFE_RIGHT) // 2, y + 13), f"{idx}. {label}", 25, WHITE, True, anchor="ma")
        draw_text(draw, (SAFE_X, y + 88), wrap(detail, 29), 28, (255, 255, 255, 238), False, 10)
        if idx == 1:
            draw_text(draw, ((SAFE_X + SAFE_RIGHT) // 2, y + 190), "↓", 42, AQUA, True, anchor="ma")
        y += 258
    footer(draw)
    return image.convert("RGB")


def slide_production(topic: Topic) -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    add_photo_background(image, topic, 4)
    draw = ImageDraw.Draw(image)
    header(draw, topic, 4, "CONTENT SYSTEM")
    title(draw, 185, "게시물은 이렇게\n전문성을 갖춥니다", 52)
    y = 420
    for idx, item in enumerate(topic.production, start=1):
        translucent_panel(draw, (SAFE_X, y, SAFE_RIGHT, y + 92), 222)
        draw_text(draw, (SAFE_X + 30, y + 26), f"{idx:02d}", 24, AQUA, True)
        draw_text(draw, (SAFE_X + 112, y + 24), wrap(item, 28), 25, INK, True, 5)
        y += 116
    footer(draw)
    return image.convert("RGB")


def slide_checklist(topic: Topic) -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    add_photo_background(image, topic, 5)
    draw = ImageDraw.Draw(image)
    header(draw, topic, 5, "SAVE THIS")
    title(draw, 180, f"{topic.pillar}\n실무 체크리스트", 50)
    y = 420
    for idx, item in enumerate(topic.checklist, start=1):
        draw.rounded_rectangle((SAFE_X, y, SAFE_X + 64, y + 58), radius=8, fill=(14, 165, 233, 230))
        draw_text(draw, (SAFE_X + 32, y + 13), str(idx), 24, WHITE, True, anchor="ma")
        draw_text(draw, (SAFE_X + 92, y + 11), wrap(item, 27), 27, WHITE, True, 5)
        y += 88
    footer(draw)
    return image.convert("RGB")


def instagram_caption_for(topic: Topic, target_date: date) -> str:
    return (
        f"{topic.instagram}\n\n"
        f"오늘의 관찰: {target_date.isoformat()}\n"
        "근거를 소비자가 이해할 수 있는 순서로 재배열하는 것이 핵심입니다."
    )


def facebook_post_for(topic: Topic) -> str:
    evidence_lines = "\n".join(f"- {name}: {fact}" for name, fact in topic.evidence)
    checklist_lines = "\n".join(f"{index}. {item}" for index, item in enumerate(topic.checklist[:4], start=1))
    return (
        f"{topic.facebook}\n\n"
        "전문가 관점:\n"
        "뷰티 브랜드 콘텐츠의 문제는 정보가 부족한 것이 아니라 정보의 위계가 정리되지 않은 경우가 많다는 점입니다. "
        "성분, 시장 기사, 사용 장면, 브랜드 운영 이슈를 같은 높이로 말하면 고객은 무엇을 먼저 믿어야 하는지 판단하기 어렵습니다.\n\n"
        "이번 콘텐츠에서 읽어야 할 시장 신호:\n"
        f"{evidence_lines}\n\n"
        "BBBB 적용 프레임:\n"
        f"{checklist_lines}\n\n"
        "결론:\n"
        "좋은 게시물은 제품을 더 크게 포장하는 것이 아니라, 고객이 선택을 검토할 수 있는 기준을 남깁니다. "
        "그래서 이미지, 카피, 근거, 채널 역할이 하나의 논리로 연결되어야 합니다."
    )


def linkedin_post_for(topic: Topic, source_lines: str) -> str:
    production_lines = "\n".join(f"{index}. {item}" for index, item in enumerate(topic.production, start=1))
    checklist_lines = "\n".join(f"- {item}" for item in topic.checklist)
    return (
        f"{topic.linkedin}\n\n"
        "왜 중요한가:\n"
        "뷰티·메디컬 스킨케어 시장에서 콘텐츠는 더 이상 단순한 홍보물이 아닙니다. "
        "성분과 효능을 말하는 동시에 규제 가능한 표현, 소비자 이해도, 채널별 구매 맥락을 함께 관리해야 하는 운영 자산입니다.\n\n"
        "실행 기준:\n"
        f"{production_lines}\n\n"
        "검토 체크리스트:\n"
        f"{checklist_lines}\n\n"
        "실무적으로는 한 개의 게시물을 만들기 전에 먼저 세 가지 질문을 확인합니다. "
        "첫째, 이 메시지가 어떤 고객 문제에서 출발하는가. 둘째, 어떤 근거까지 말할 수 있는가. "
        "셋째, Instagram, Facebook, LinkedIn에서 각각 어떤 역할로 번역되는가.\n\n"
        "참고 기사:\n"
        f"{source_lines}"
    )


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
    (out / "facebook-caption.txt").write_text(facebook_post_for(topic), encoding="utf-8")
    (out / "linkedin-post.txt").write_text(linkedin_post_for(topic, source_lines), encoding="utf-8")
    (out / "reddit-title.txt").write_text(topic.x_post, encoding="utf-8")
    (out / "reddit-post.txt").write_text(linkedin_post_for(topic, source_lines), encoding="utf-8")
    (out / "x-post.txt").write_text(topic.x_post, encoding="utf-8")
    (out / "x-thread.txt").write_text("\n---\n".join((topic.x_post, topic.hook, *topic.checklist[:3])), encoding="utf-8")
    (out / "x-mode.txt").write_text(("short", "image", "thread", "short", "image")[target_date.toordinal() % 5], encoding="utf-8")
    (out / "sources.json").write_text(
        json.dumps([source.__dict__ for source in topic.sources], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out / "README.md").write_text(
        f"# {target_date.isoformat()} Daily Content\n\n"
        f"- Pillar: {topic.pillar}\n"
        f"- Source: Hankyung market signal\n"
        f"- Format: 5-slide professional carousel\n\n{source_lines}\n",
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
