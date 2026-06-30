#!/usr/bin/env python3
"""Generate a date-specific bbbb.beauty social package for the daily workflow."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
import math
import os
from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ANCHOR_DATE = date(2026, 6, 22)
NAVY = "#1E293B"
BEIGE = "#F8F6F2"
WHITE = "#FFFFFF"
MUTED = "#475569"
AQUA = "#0EA5E9"
SOFT_AQUA = "#BAE6FD"
SKIN = "#E8D8C8"
CLAY = "#C9A58F"

WIDTH = 1080
HEIGHT = 1080
SAFE_X = 128
CONTENT_RIGHT = 952


@dataclass(frozen=True)
class Topic:
    slug: str
    pillar: str
    label: str
    headline: str
    questions: tuple[str, str, str]
    instagram: str
    facebook: str
    linkedin: str
    x_post: str


TOPICS = (
    Topic(
        "evidence-translation",
        "Evidence Translation",
        "SCIENCE TO UNDERSTANDING",
        "과학적 근거는\n많이 말하는 것이 아니라\n정확히 이해시키는 일입니다.",
        (
            "어떤 근거가\n핵심인가?",
            "누가 이해해야\n하는가?",
            "어떤 장면으로\n검증할까?",
        ),
        "근거를 나열하기 전에, 고객이 이해해야 할 하나의 작용 원리를 고릅니다. 과학의 정확성과 이해의 흐름은 함께 설계할 수 있습니다.",
        "더마코스메틱 콘텐츠에서 근거는 장식이 아니라 신뢰의 구조입니다. 문헌과 핵심 경로를 먼저 정리하고, 그중 브랜드가 설명해야 할 하나의 변화를 선택해야 합니다.",
        "문제:\n과학적 근거가 많아도 고객이 무엇을 이해해야 하는지 선명하지 않을 수 있습니다.\n\n해결:\n핵심 근거, 대상, 검증 장면의 순서로 설명 구조를 설계합니다.\n\n실행:\n1. 어떤 근거가 핵심인가\n2. 누가 이해해야 하는가\n3. 어떤 장면으로 검증할까\n\n이 프레임은 의학적 효능을 보장하지 않으며, 정확한 과학 커뮤니케이션을 위한 제작 기준입니다.",
        "과학을 신뢰로 바꾸는 첫 단계는 핵심 근거를 하나로 정하는 일입니다.",
    ),
    Topic(
        "mechanism-in-motion",
        "Mechanism in Motion",
        "MOA / MOD VISUALIZATION",
        "작용 기전은\n복잡하게 보이는 것이 아니라\n정확하게 보여야 합니다.",
        (
            "어떤 변화가\n시작되는가?",
            "어떤 순서로\n이어지는가?",
            "무엇을 오해 없이\n보여줄까?",
        ),
        "보이지 않는 작용 기전은 정확한 순서와 명확한 장면으로 설명됩니다. 복잡한 생물학적 과정을 이해 가능한 흐름으로 바꿔보세요.",
        "MoA·MoD 시각화의 핵심은 화려한 3D가 아닙니다. 분자 구조와 핵심 경로를 검토한 뒤, 변화의 순서와 표현 범위를 정확히 정하는 일입니다.",
        "문제:\n보이지 않는 생물학적 과정은 텍스트만으로 설명하기 어렵습니다.\n\n해결:\n변화의 시작, 과정, 표현 범위를 장면으로 설계합니다.\n\n실행:\n한 장면에는 하나의 변화만 배치하고, 전환마다 다음 단계의 이유를 연결합니다.",
        "좋은 MoA 영상은 복잡함을 줄이는 대신 정확한 순서를 남깁니다.",
    ),
    Topic(
        "visual-learning",
        "Visual Learning",
        "EDUCATIONAL CONTENT",
        "교육 콘텐츠는\n정보를 많이 주는 것이 아니라\n이해의 순서를 만듭니다.",
        (
            "누가 먼저\n이해해야 하는가?",
            "무엇을 직접\n조작하게 할까?",
            "어떤 결정을\n돕는가?",
        ),
        "교육 콘텐츠는 정보를 더하는 방식보다 사용자가 이해하고 다음 질문으로 넘어가는 흐름이 중요합니다. 학습자, 상호작용, 결정을 먼저 정리해보세요.",
        "질환과 성분 교육은 설명을 길게 만드는 일이 아니라, 사용자가 이해할 순서와 질문을 설계하는 일입니다. 교육 플랫폼과 마이크로사이트는 그 흐름을 반복 가능한 자산으로 만듭니다.",
        "문제:\n전문 정보가 많을수록 학습자는 핵심 경로를 놓치기 쉽습니다.\n\n해결:\n학습자, 상호작용, 의사결정의 순서로 콘텐츠를 설계합니다.\n\n실행:\n한 화면에는 한 질문만 두고, 다음 화면에서 사용자가 직접 확인할 근거를 연결합니다.",
        "교육은 정보 전달이 아니라 이해 가능한 사용 여정을 만드는 일입니다.",
    ),
    Topic(
        "documentary-trust",
        "Documentary Trust",
        "SCIENCE WITH CREDIBILITY",
        "과학의 신뢰는\n주장보다\n보여주는 방식에서 시작됩니다.",
        (
            "누가 말하는가?",
            "무엇을 현장에서\n보여줄까?",
            "어떤 맥락을\n남길까?",
        ),
        "과학 콘텐츠의 신뢰는 설명의 길이보다, 누가 무엇을 어떤 맥락에서 보여주는지에 달려 있습니다. 영화적 시선은 전문성과 브랜드의 거리를 줄일 수 있습니다.",
        "다큐멘터리 형식은 과학적 전문성과 브랜드의 맥락을 함께 보여주는 방식입니다. 인터뷰, 현장, 제품의 역할을 하나의 내러티브로 연결할 때 신뢰는 더 구체적으로 전달됩니다.",
        "문제:\n전문성이 높은 메시지는 브랜드 언어와 분리되어 보이기 쉽습니다.\n\n해결:\n화자, 현장, 맥락을 하나의 이야기로 연결합니다.\n\n실행:\n한 편의 영상에서 증명할 질문 하나를 정하고, 그 질문을 뒷받침할 사람과 장면을 배치합니다.",
        "신뢰는 큰 주장보다 더 구체적인 장면에서 시작됩니다.",
    ),
    Topic(
        "immersive-experience",
        "Immersive Experience",
        "AR + INTERACTIVE",
        "복잡한 기술은\n설명만으로 남지 않습니다.\n직접 탐색될 때 기억됩니다.",
        (
            "무엇을 직접\n탐색하게 할까?",
            "어디에서\n몰입이 필요한가?",
            "어떤 환경으로\n확장할까?",
        ),
        "AR과 인터랙티브 콘텐츠는 보이지 않는 기술을 사용자가 직접 탐색하게 합니다. 제품 출시, 교육, 박람회에서 어떤 경험이 필요한지부터 정해보세요.",
        "증강현실, 인터랙티브 애니메이션, 3D 모델은 복잡한 과학을 체험 가능한 장면으로 바꿉니다. 중요한 것은 기술 자체가 아니라 사용자가 무엇을 탐색하고 이해할지입니다.",
        "문제:\n제품의 구조와 작용 원리는 정적인 자료만으로 충분히 전달되지 않을 수 있습니다.\n\n해결:\n탐색 대상, 몰입 시간, 사용 환경을 먼저 정합니다.\n\n실행:\n사용자가 한 번의 조작으로 확인해야 할 핵심 정보를 정의하고, 그 정보에 맞는 인터랙션을 설계합니다.",
        "인터랙티브 경험의 목적은 기술을 과시하는 것이 아니라 이해를 직접 만들어내는 일입니다.",
    ),
    Topic(
        "media-art-systems",
        "Media Art Systems",
        "SPACE + SCREEN + SOUND",
        "미디어아트는\n화면을 채우는 일이 아니라\n공간의 흐름을 만드는 일입니다.",
        (
            "사람은 어디에서\n만나는가?",
            "어떤 매체가\n역할에 맞는가?",
            "무엇을 경험으로\n남기는가?",
        ),
        "미디어아트는 화면, 사운드, 공간, 이동이 하나의 경험으로 작동할 때 의미가 생깁니다. 매체보다 먼저 관객의 흐름을 설계해보세요.",
        "미디어 파사드, 프로젝션 매핑, 사운드 디자인은 각각의 기술이 아니라 공간 경험을 구성하는 재료입니다. 관객이 만나는 순서와 브랜드가 남길 장면을 먼저 정해야 합니다.",
        "문제:\n화면과 기술이 많아도 관객의 경험이 하나로 연결되지 않을 수 있습니다.\n\n해결:\n만남, 매체의 역할, 기억의 장면의 순서로 공간을 설계합니다.\n\n실행:\n관객의 이동 경로에서 가장 중요한 한 장면을 정하고, 다른 매체는 그 장면을 돕도록 배치합니다.",
        "좋은 미디어아트는 매체를 늘리는 대신 경험의 중심을 선명하게 만듭니다.",
    ),
    Topic(
        "scientific-production",
        "Scientific Production",
        "RESEARCH TO FINAL",
        "과학 콘텐츠의 완성도는\n마지막 렌더가 아니라\n처음 검토에서 결정됩니다.",
        (
            "무엇을 문헌으로\n확인할까?",
            "어디에서 흐름을\n검토할까?",
            "어떤 형식으로\n전달할까?",
        ),
        "과학 콘텐츠는 리서치, 스크립트, 스토리보드, 애니매틱을 거쳐 정확성과 흐름을 함께 검토할 때 완성됩니다. 렌더 전에 결정해야 할 것을 정리해보세요.",
        "메디컬 콘텐츠 제작은 리서치에서 파이널까지 정확성과 시각적 완성도를 함께 검토하는 과정입니다. 스크립트와 스토리보드, 애니매틱 단계에서 표현 범위를 확인해야 최종 결과물의 신뢰가 흔들리지 않습니다.",
        "문제:\n최종 렌더 단계에서 과학적 표현과 이야기 흐름을 함께 고치기에는 늦을 수 있습니다.\n\n해결:\n리서치, 스크립트, 스토리보드, 애니매틱의 검토 지점을 분명히 둡니다.\n\n실행:\n다음 제작 전에 각 단계에서 확인할 과학적 사실과 표현 범위를 한 문장씩 기록합니다.",
        "과학적 정확성은 마지막 검수가 아니라 제작 전 과정의 기준입니다.",
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


def text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    value: str,
    size: int,
    fill: str,
    bold: bool = False,
    spacing: int = 10,
    anchor: str | None = None,
) -> None:
    draw.multiline_text(xy, value, font=font(size, bold), fill=fill, spacing=spacing, anchor=anchor)


def wrapped(value: str, width: int = 23) -> str:
    return "\n".join(textwrap.wrap(" ".join(value.split()), width=width, break_long_words=False))


def fit_text(draw: ImageDraw.ImageDraw, value: str, max_width: int, start_size: int, min_size: int, bold: bool) -> int:
    size = start_size
    while size > min_size:
        box = draw.multiline_textbbox((0, 0), value, font=font(size, bold), spacing=8)
        if box[2] - box[0] <= max_width:
            return size
        size -= 2
    return min_size


def rounded_rectangle(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int, fill: str, outline: str | None = None, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def add_gradient_background(image: Image.Image, topic: Topic, page: int) -> None:
    pixels = image.load()
    top = tuple(int(BEIGE[i : i + 2], 16) for i in (1, 3, 5))
    bottom = (232, 221, 211)
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        for x in range(WIDTH):
            glow = 0.06 * math.sin((x + page * 57) / 90) + 0.04 * math.cos((y + page * 43) / 130)
            ratio = max(0, min(1, t + glow))
            pixels[x, y] = tuple(int(top[i] * (1 - ratio) + bottom[i] * ratio) for i in range(3))

    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    accent_x = 650 + (page % 3) * 38
    draw.ellipse((accent_x, 110, accent_x + 520, 630), fill=(14, 165, 233, 28))
    draw.ellipse((760, 480, 1180, 1060), fill=(201, 165, 143, 52))
    draw.ellipse((-180, 650, 330, 1170), fill=(255, 255, 255, 80))
    draw.rounded_rectangle((740, 146, 1000, 470), radius=70, fill=(255, 255, 255, 82))
    draw.rounded_rectangle((812, 208, 910, 560), radius=48, fill=(30, 41, 59, 190))
    draw.rounded_rectangle((835, 162, 887, 236), radius=22, fill=(14, 165, 233, 190))
    draw.ellipse((675, 352, 745, 422), outline=(255, 255, 255, 160), width=5)
    draw.ellipse((948, 582, 1015, 649), outline=(14, 165, 233, 150), width=5)
    for idx in range(9):
        x = 690 + idx * 38
        y = 720 + int(math.sin(idx + page) * 36)
        draw.line((x, y, x + 46, y + 28), fill=(30, 41, 59, 70), width=3)
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(14, 165, 233, 150))
    image.alpha_composite(overlay)


def header(draw: ImageDraw.ImageDraw, topic: Topic, page: int) -> None:
    rounded_rectangle(draw, (88, 70, 992, 132), 31, NAVY)
    text(draw, (122, 91), f"bbbb / {topic.pillar.upper()}", 18, WHITE, True)
    text(draw, (918, 91), f"{page:02d}/05", 18, AQUA, True)


def badge(draw: ImageDraw.ImageDraw, xy: tuple[int, int], label: str) -> None:
    x, y = xy
    box = draw.textbbox((0, 0), label, font=font(16, True))
    width = box[2] - box[0] + 42
    rounded_rectangle(draw, (x, y, x + width, y + 42), 21, NAVY)
    text(draw, (x + 21, y + 11), label, 16, WHITE, True)


def footer(draw: ImageDraw.ImageDraw) -> None:
    text(draw, (SAFE_X, 1008), "BBBB BEAUTY INTELLIGENCE", 15, MUTED, True)
    rounded_rectangle(draw, (780, 1000, 952, 1029), 14, NAVY)
    text(draw, (806, 1007), "SAVE / SHARE", 13, WHITE, True)


def question_support(topic: Topic, question: str, action: str) -> str:
    clean = question.replace(chr(10), " ")
    return f"{topic.pillar}에서는\n{clean}를 먼저 정하고\n{action}를 한 장면에 남깁니다."


def slide(topic: Topic, page: int, eyebrow: str, title: str, body: str) -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), BEIGE)
    add_gradient_background(image, topic, page)
    draw = ImageDraw.Draw(image)
    header(draw, topic, page)
    badge(draw, (SAFE_X, 184), eyebrow)

    panel_top = 256
    panel_bottom = 824
    rounded_rectangle(draw, (92, panel_top, 988, panel_bottom), 42, (255, 255, 255, 210), outline=(255, 255, 255, 230), width=2)
    draw.rectangle((92, panel_top, 116, panel_bottom), fill=AQUA)

    max_title_width = CONTENT_RIGHT - SAFE_X
    title_size = fit_text(draw, title, max_title_width, 54, 39, True)
    text(draw, (SAFE_X, 322), title, title_size, NAVY, True, 9)

    wrapped_body = wrapped(body, 25)
    text(draw, (SAFE_X, 686), wrapped_body, 27, MUTED, False, 8)
    footer(draw)
    return image.convert("RGB")


def create_package(target_date: date, out_root: Path) -> Path:
    index = (target_date - ANCHOR_DATE).days % len(TOPICS)
    topic = TOPICS[index]
    out = out_root / f"{target_date.isoformat()}-{topic.slug}"
    carousel = out / "carousel"
    carousel.mkdir(parents=True, exist_ok=True)

    slides = [
        slide(topic, 1, topic.label, topic.headline, topic.instagram),
        slide(topic, 2, "QUESTION 01", topic.questions[0], question_support(topic, topic.questions[0], "핵심 근거")),
        slide(topic, 3, "QUESTION 02", topic.questions[1], question_support(topic, topic.questions[1], "이해의 순서")),
        slide(topic, 4, "QUESTION 03", topic.questions[2], question_support(topic, topic.questions[2], "표현의 범위")),
        slide(topic, 5, "SAVE THIS", f"{topic.pillar}\n체크리스트", "세 질문을 먼저 확인한 뒤 리서치와 제작의 순서를 정리합니다."),
    ]
    for page, image in enumerate(slides, start=1):
        image.save(carousel / f"{page:02d}.png", quality=95)

    (out / "instagram-caption.txt").write_text(topic.instagram, encoding="utf-8")
    (out / "facebook-caption.txt").write_text(topic.facebook, encoding="utf-8")
    (out / "linkedin-post.txt").write_text(topic.linkedin, encoding="utf-8")
    (out / "x-post.txt").write_text(topic.x_post, encoding="utf-8")
    (out / "x-thread.txt").write_text("\n---\n".join((topic.x_post, *topic.questions)), encoding="utf-8")
    modes = ("short", "image", "thread", "short", "image")
    (out / "x-mode.txt").write_text(modes[target_date.toordinal() % len(modes)], encoding="utf-8")
    (out / "README.md").write_text(
        f"# {target_date.isoformat()} Daily Content\n\n- Pillar: {topic.pillar}\n- Topic: {topic.headline.replace(chr(10), ' ')}\n- Format: 5-slide carousel\n",
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
