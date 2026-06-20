from __future__ import annotations

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "artifacts" / "2026-06-20-creative-leadership-note"

CREAM = "#F5F1E8"
INK = "#101214"
MUTED = "#5B6168"
RED = "#C8442D"
BLUE = "#1565C0"
SAGE = "#7A8B5A"
PAPER = "#FFFDFC"


def first_existing(paths: list[str]) -> Path:
    for raw in paths:
        if raw and Path(raw).is_file():
            return Path(raw)
    raise FileNotFoundError("No usable font found.")


FONT_REGULAR = first_existing(
    [os.getenv("FONT_REGULAR", ""), r"C:\Windows\Fonts\NotoSansKR-VF.ttf", r"C:\Windows\Fonts\malgun.ttf"]
)
FONT_BOLD = first_existing(
    [os.getenv("FONT_BOLD", ""), r"C:\Windows\Fonts\malgunbd.ttf", r"C:\Windows\Fonts\NotoSansKR-VF.ttf"]
)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REGULAR), size)


def text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    value: str,
    size: int,
    fill: str = INK,
    *,
    bold: bool = False,
    spacing: int = 8,
) -> None:
    draw.multiline_text(xy, value, font=font(size, bold), fill=fill, spacing=spacing)


def card(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    label: str,
    title: str,
    body: str,
    accent: str,
) -> None:
    x0, y0, _, _ = box
    draw.rounded_rectangle(box, radius=28, fill=PAPER, outline=INK, width=3)
    draw.rounded_rectangle((x0 + 24, y0 + 20, x0 + 224, y0 + 66), radius=18, fill=accent)
    text(draw, (x0 + 44, y0 + 32), label, 20, PAPER, bold=True)
    text(draw, (x0 + 28, y0 + 94), title, 36, INK, bold=True)
    # Body copy is kept to two lines and begins high enough to clear the title.
    text(draw, (x0 + 28, y0 + 164), body, 20, MUTED, spacing=6)


def create_image() -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    image_path = OUT / "creative-leadership-note.png"
    img = Image.new("RGB", (1080, 1350), CREAM)
    draw = ImageDraw.Draw(img)

    for x in range(0, 1081, 54):
        draw.line((x, 0, x, 1350), fill="#E7DED0", width=1)
    for y in range(0, 1351, 54):
        draw.line((0, y, 1080, y), fill="#E7DED0", width=1)

    draw.rectangle((0, 0, 1080, 112), fill=INK)
    text(draw, (72, 32), "SATURDAY CREATIVE NOTE / CREATIVE LEADERSHIP", 26, PAPER, bold=True)
    text(
        draw,
        (72, 156),
        "좋은 크리에이티브 팀은\n프롬프트보다 리뷰 질문을\n먼저 설계합니다.",
        60,
        INK,
        bold=True,
    )
    text(draw, (72, 390), "팀의 판단을 선명하게 만드는\n운영 질문 4가지입니다.", 25, MUTED, spacing=6)

    card(
        draw,
        (72, 490, 504, 744),
        "QUESTION 01",
        "Use Case",
        "이 작업은 어떤 의사결정을\n빠르고 정확하게 만드나?",
        RED,
    )
    card(
        draw,
        (576, 490, 1008, 744),
        "QUESTION 02",
        "Tools",
        "어떤 도구가 맥락 수집과\n실행을 분리해 주나?",
        BLUE,
    )
    card(
        draw,
        (72, 790, 504, 1044),
        "QUESTION 03",
        "Instructions",
        "어떤 지시가 모호함을\n구체적 행동으로 바꾸나?",
        SAGE,
    )
    card(
        draw,
        (576, 790, 1008, 1044),
        "QUESTION 04",
        "Guardrails",
        "어떤 검수 기준이\n끝까지 지켜지나?",
        INK,
    )

    draw.rectangle((72, 1110, 1008, 1176), fill=INK)
    text(draw, (104, 1132), "SOURCE", 18, PAPER, bold=True)
    text(draw, (218, 1132), "OpenAI | Practical guide to building agents", 18, PAPER, bold=True)
    text(draw, (72, 1202), "bbbb / Creative Leadership / June 20, 2026", 18, MUTED, bold=True)
    img.save(image_path, quality=95)
    return image_path


if __name__ == "__main__":
    print(create_image())
