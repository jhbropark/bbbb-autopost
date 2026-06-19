from __future__ import annotations

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "artifacts" / "2026-06-19-linkedin-framework"

BLACK = "#080808"
WHITE = "#ffffff"
PAPER = "#f6f6f1"
CYAN = "#00d6c9"
PINK = "#ff2e88"
ACID = "#d6ff00"
GRAY = "#5d666b"
GRID = "#dfe4e4"


def first_existing(paths: list[str]) -> Path:
    for raw in paths:
        if not raw:
            continue
        path = Path(raw)
        if path.is_file():
            return path
    raise FileNotFoundError("No usable font found. Set FONT_REGULAR/FONT_BOLD or install Noto Sans KR.")


FONT_REGULAR = first_existing(
    [
        os.getenv("FONT_REGULAR", ""),
        r"C:\Windows\Fonts\NotoSansKR-VF.ttf",
        r"C:\Windows\Fonts\malgun.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
)
FONT_BOLD = first_existing(
    [
        os.getenv("FONT_BOLD", ""),
        r"C:\Windows\Fonts\malgunbd.ttf",
        r"C:\Windows\Fonts\NotoSansKR-VF.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REGULAR), size)


def text(draw: ImageDraw.ImageDraw, xy, value: str, size: int, fill=BLACK, bold=False, anchor=None, spacing=10):
    draw.multiline_text(xy, value, font=font(size, bold), fill=fill, anchor=anchor, spacing=spacing)


def grid(draw: ImageDraw.ImageDraw) -> None:
    for x in range(0, 1200, 60):
        draw.line((x, 0, x, 1200), fill=GRID, width=1)
    for y in range(0, 1200, 60):
        draw.line((0, y, 1200, y), fill=GRID, width=1)


def make_card() -> Image.Image:
    img = Image.new("RGB", (1200, 1200), PAPER)
    draw = ImageDraw.Draw(img)
    grid(draw)

    draw.rectangle((0, 0, 1200, 132), fill=BLACK)
    text(draw, (72, 43), "bbbb / LINKEDIN FRAMEWORK", 31, WHITE, True)
    text(draw, (1128, 48), "HOW", 26, CYAN, True, "ra")

    draw.rectangle((72, 188, 430, 244), fill=BLACK)
    draw.rectangle((72, 188, 86, 244), fill=PINK)
    text(draw, (105, 205), "BEAUTY BRAND HYPOTHESIS", 20, WHITE, True)

    text(draw, (72, 300), "Beauty Brand\nHypothesis\nFramework", 64, BLACK, True, spacing=12)
    text(draw, (74, 565), "A strong beauty brand is not louder.\nIt is easier to verify.", 28, GRAY, False, spacing=12)

    items = [
        ("01", "Customer Problem", "고객이 실제로 느끼는 불편"),
        ("02", "Product Proof", "제품이 보여줄 수 있는 근거"),
        ("03", "Sensory Signal", "선택을 돕는 감각 신호"),
        ("04", "Brand Language", "기억되는 문장과 기준"),
        ("05", "Channel Behavior", "채널별 행동 설계"),
    ]

    x0, y0 = 620, 250
    for i, (num, title, desc) in enumerate(items):
        y = y0 + i * 132
        fill = BLACK if i == 1 else WHITE
        ink = WHITE if i == 1 else BLACK
        draw.rectangle((x0, y, 1110, y + 92), fill=fill, outline=BLACK, width=3)
        draw.rectangle((x0, y, x0 + 18, y + 92), fill=CYAN if i % 2 == 0 else PINK)
        text(draw, (x0 + 48, y + 24), num, 22, CYAN if fill == BLACK else GRAY, True)
        text(draw, (x0 + 112, y + 18), title, 28, ink, True)
        text(draw, (x0 + 112, y + 54), desc, 20, WHITE if fill == BLACK else GRAY, False)

    draw.line((72, 880, 1110, 880), fill=BLACK, width=3)
    text(draw, (72, 930), "Use this before visual identity, package design, or content production.", 25, BLACK, True)
    draw.rectangle((72, 1022, 530, 1090), fill=ACID)
    text(draw, (301, 1056), "PROBLEM → PROOF → SIGNAL", 24, BLACK, True, "mm")
    text(draw, (1128, 1068), "RADICAL LABORATORY", 18, BLACK, True, "ra")

    return img


def create_text() -> str:
    return """뷰티 브랜드를 만들 때 가장 먼저 정리해야 할 것은 디자인 취향이 아니라 검증 가능한 가설입니다.

저는 브랜드를 볼 때 다섯 가지를 먼저 봅니다.

1. 고객이 실제로 느끼는 문제
2. 제품이 보여줄 수 있는 근거
3. 선택을 돕는 감각 신호
4. 기억되는 브랜드 언어
5. 채널별 행동 설계

이 순서가 없으면 좋은 원료, 좋은 패키지, 좋은 이미지도 서로 따로 움직입니다.

강한 브랜드는 더 크게 말하는 브랜드가 아니라 더 쉽게 검증되는 브랜드입니다."""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    make_card().save(OUT / "linkedin-framework-card.png", quality=95)
    (OUT / "linkedin-post.txt").write_text(create_text(), encoding="utf-8")
    (OUT / "README.md").write_text(
        "# LinkedIn Framework Post\n\n"
        "- Format: 1:1 framework card, 1200 x 1200\n"
        "- Purpose: LinkedIn test post replacing reused Instagram carousel image\n"
        "- Role: Experience Innovation Director / how\n",
        encoding="utf-8",
    )
    print(OUT)


if __name__ == "__main__":
    main()
