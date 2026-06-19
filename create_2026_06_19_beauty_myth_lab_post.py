from __future__ import annotations

import math
import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "artifacts" / "2026-06-19-beauty-myth-lab"

BLACK = "#080808"
WHITE = "#ffffff"
PAPER = "#f7f7f2"
CYAN = "#00d6c9"
PINK = "#ff2e88"
ACID = "#d6ff00"
GRAY = "#596166"
LIGHT = "#dde2e2"


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


def write_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    value: str,
    size: int,
    fill: str = BLACK,
    bold: bool = False,
    anchor: str | None = None,
    spacing: int = 12,
) -> None:
    draw.multiline_text(
        xy,
        value,
        font=font(size, bold),
        fill=fill,
        anchor=anchor,
        spacing=spacing,
    )


def grid(draw: ImageDraw.ImageDraw) -> None:
    for x in range(0, 1080, 54):
        draw.line((x, 0, x, 1350), fill=LIGHT, width=1)
    for y in range(0, 1350, 54):
        draw.line((0, y, 1080, y), fill=LIGHT, width=1)


def header(draw: ImageDraw.ImageDraw, page: int) -> None:
    draw.rectangle((0, 0, 1080, 140), fill=BLACK)
    write_text(draw, (72, 48), "bbbb / BEAUTY MYTH LAB", 36, WHITE, True)
    write_text(draw, (1008, 63), f"{page:02d} / 06", 24, CYAN, True, "ra")


def footer(draw: ImageDraw.ImageDraw) -> None:
    draw.rectangle((0, 1245, 1080, 1350), fill=BLACK)
    write_text(draw, (72, 1278), "RADICAL LABORATORY", 18, WHITE, True)
    write_text(draw, (1008, 1278), "SCIENCE TO MESSAGE", 18, CYAN, True, "ra")


def tag(draw: ImageDraw.ImageDraw, value: str, y: int = 184) -> None:
    bbox = draw.textbbox((0, 0), value, font=font(21, True))
    width = bbox[2] - bbox[0] + 56
    draw.rectangle((72, y, 72 + width, y + 52), fill=BLACK)
    draw.rectangle((72, y, 84, y + 52), fill=PINK)
    write_text(draw, (102, y + 11), value, 21, WHITE, True)


def molecule(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], seed: int) -> None:
    rng = np.random.default_rng(seed)
    x0, y0, x1, y1 = box
    points = [(int(rng.uniform(x0, x1)), int(rng.uniform(y0, y1))) for _ in range(24)]
    for i, p in enumerate(points):
        linked = sorted(((math.dist(p, q), q) for q in points if q != p), key=lambda item: item[0])[:2]
        for _, q in linked:
            draw.line((*p, *q), fill=CYAN if i % 2 else PINK, width=2)
    for i, (x, y) in enumerate(points):
        r = 7 if i % 5 else 13
        draw.rectangle((x - r, y - r, x + r, y + r), fill=BLACK if i % 5 else ACID, outline=BLACK, width=2)


def formula_strip(draw: ImageDraw.ImageDraw, labels: list[str], y: int) -> None:
    x = 90
    for i, label in enumerate(labels):
        fill = BLACK if i == 1 else WHITE
        ink = WHITE if i == 1 else BLACK
        draw.rectangle((x, y, x + 185, y + 98), fill=fill, outline=BLACK, width=3)
        write_text(draw, (x + 92, y + 49), label, 24, ink, True, "mm")
        if i < len(labels) - 1:
            draw.line((x + 185, y + 49, x + 235, y + 49), fill=PINK if i % 2 else CYAN, width=7)
        x += 235


def checklist(draw: ImageDraw.ImageDraw, items: list[str], y: int) -> None:
    for i, item in enumerate(items):
        yy = y + i * 92
        draw.rectangle((105, yy, 975, yy + 68), fill=WHITE, outline=BLACK, width=2)
        draw.rectangle((105, yy, 126, yy + 68), fill=CYAN if i % 2 == 0 else PINK)
        write_text(draw, (160, yy + 34), item, 27, BLACK, True, "lm")


def slide(page: int, kicker: str, title: str, body: str, mode: str) -> Image.Image:
    img = Image.new("RGB", (1080, 1350), PAPER)
    draw = ImageDraw.Draw(img)
    grid(draw)
    header(draw, page)
    tag(draw, kicker)
    write_text(draw, (1008, 172), f"{page:02d}", 122, LIGHT, True, "ra")
    title_xy = (72, 292)
    draw.multiline_text(title_xy, title, font=font(62, True), fill=BLACK, spacing=18)
    title_box = draw.multiline_textbbox(title_xy, title, font=font(62, True), spacing=18)
    body_y = max(510, title_box[3] + 40)
    write_text(draw, (72, body_y), body, 30, GRAY, False, spacing=16)

    if mode == "cover":
        molecule(draw, (85, 735, 995, 1115), 19)
        draw.rectangle((72, 1045, 1008, 1140), fill=BLACK)
        draw.rectangle((72, 1045, 92, 1140), fill=PINK)
        write_text(draw, (120, 1092), "A beauty brand starts with a testable hypothesis.", 25, WHITE, True, "lm")
    elif mode == "myths":
        checklist(draw, ["비싼 원료 = 좋은 브랜드", "예쁜 패키지 = 명확한 차별점", "트렌드 컬러 = 시장성"], 760)
        draw.line((150, 745, 930, 1085), fill=PINK, width=10)
    elif mode == "formula":
        formula_strip(draw, ["가설", "증거", "감각", "언어"], 800)
        write_text(draw, (540, 990), "좋은 브랜드는 주장보다 검증 가능한 구조를 먼저 만듭니다.", 30, BLACK, True, "ma")
    elif mode == "lab":
        molecule(draw, (105, 720, 520, 1110), 31)
        draw.rectangle((590, 770, 965, 1075), fill=BLACK)
        write_text(draw, (635, 825), "QUESTION", 24, CYAN, True)
        write_text(draw, (635, 890), "고객은 무엇을\n믿어야 하는가?", 38, WHITE, True, spacing=18)
    elif mode == "content":
        checklist(draw, ["Instagram: 보이는 실험", "Facebook: 왜 그런지 설명", "LinkedIn: 실행 방법 정리"], 755)
        draw.rectangle((170, 1090, 910, 1152), fill=ACID)
        write_text(draw, (540, 1121), "WHAT / WHY / HOW", 28, BLACK, True, "mm")
    elif mode == "cta":
        draw.rectangle((105, 740, 975, 1088), fill=BLACK)
        draw.rectangle((105, 740, 127, 1088), fill=PINK)
        write_text(draw, (160, 805), "PROJECT CHECK", 24, CYAN, True)
        write_text(draw, (160, 875), "브랜드가 증명해야 할\n가설은 무엇인가요?", 42, WHITE, True, spacing=18)
        draw.rectangle((260, 1130, 820, 1205), fill=CYAN)
        write_text(draw, (540, 1167), "DM으로 프로젝트 문의", 29, BLACK, True, "mm")

    footer(draw)
    return img


def create_images() -> None:
    slides = [
        (
            "BEAUTY MYTH LAB",
            "좋은 뷰티 브랜드는\n예쁜 말보다\n명확한 가설에서 시작됩니다.",
            "Radical Laboratory는 뷰티를 감각으로만 보지 않습니다.\n제품, 고객, 증거, 언어를 하나의 실험 구조로 봅니다.",
            "cover",
        ),
        (
            "MYTH 01",
            "브랜드를 약하게 만드는\n세 가지 착각",
            "원료, 패키지, 트렌드만으로는 브랜드가 완성되지 않습니다.\n고객이 믿을 수 있는 이유가 먼저 설계되어야 합니다.",
            "myths",
        ),
        (
            "METHOD",
            "우리는 브랜드를\n공식처럼 분해합니다.",
            "무엇을 주장할지보다 먼저 봐야 할 것은\n그 주장을 가능하게 만드는 증거와 감각의 연결입니다.",
            "formula",
        ),
        (
            "LAB QUESTION",
            "실험실의 질문은\n항상 하나입니다.",
            "이 제품은 왜 존재해야 하는가?\n고객은 어떤 장면에서 그것을 이해하고 선택하는가?",
            "lab",
        ),
        (
            "CHANNEL SYSTEM",
            "하나의 가설은\n채널마다 다르게 번역됩니다.",
            "같은 브랜드 아이디어라도 Instagram, Facebook, LinkedIn은\n서로 다른 역할로 설계되어야 합니다.",
            "content",
        ),
        (
            "BBBB METHOD",
            "브랜드를\n실험 가능한 시스템으로\n만듭니다.",
            "BBBB는 뷰티 브랜드의 메시지를\n시각, 콘텐츠, 경험으로 확장하는 실험실입니다.",
            "cta",
        ),
    ]
    carousel = OUT / "carousel"
    carousel.mkdir(parents=True, exist_ok=True)
    for index, args in enumerate(slides, 1):
        slide(index, *args).save(carousel / f"{index:02d}.png", quality=95)


def create_texts() -> None:
    instagram = """좋은 뷰티 브랜드는 예쁜 말보다 명확한 가설에서 시작됩니다.

BBBB는 제품, 고객, 증거, 감각을 하나의 실험 구조로 보고 브랜드 메시지로 번역합니다.

#bbbbbeauty #BeautyMythLab #RadicalLaboratory #BeautyBranding #브랜드전략 #뷰티마케팅"""

    facebook = """좋은 뷰티 브랜드는 예쁜 제품 설명에서 시작되지 않습니다. 먼저 필요한 것은 “이 브랜드가 고객에게 무엇을 증명해야 하는가”라는 가설입니다.

뷰티 시장에서 많은 브랜드가 원료, 패키지, 트렌드 컬러를 차별점으로 말합니다. 하지만 고객은 더 구체적인 이유를 필요로 합니다. 왜 이 제품이 존재해야 하는지, 어떤 장면에서 선택되어야 하는지, 어떤 감각과 언어로 기억되어야 하는지가 정리되어야 합니다.

BBBB의 Radical Laboratory 방향은 브랜드를 감각만으로 다루지 않습니다. 제품의 주장, 고객의 문제, 증거가 되는 정보, 시각적 경험을 하나의 실험 구조로 연결합니다.

Instagram에서는 이 가설을 보이는 실험으로 만들고, Facebook에서는 왜 이 구조가 필요한지 설명하며, LinkedIn에서는 실제 브랜드 시스템으로 구현하는 방법을 정리합니다.

결국 강한 뷰티 브랜드는 더 크게 말하는 브랜드가 아니라, 더 명확하게 증명하는 브랜드입니다."""

    linkedin = """문제: 뷰티 브랜드는 자주 원료, 패키지, 트렌드 컬러를 차별점으로 말합니다. 하지만 이것만으로는 고객이 브랜드를 선택해야 할 이유가 충분히 만들어지지 않습니다.

해결: 브랜드를 하나의 실험 가능한 가설로 정리해야 합니다. 이 제품은 왜 존재하는가, 고객은 어떤 상황에서 이 브랜드를 이해하는가, 어떤 증거와 감각이 선택을 만든다는 질문에서 시작해야 합니다.

실행: BBBB의 Radical Laboratory 방향은 브랜드 메시지를 `가설 -> 증거 -> 감각 -> 언어 -> 채널 콘텐츠` 순서로 분해합니다. Instagram은 시각적 실험, Facebook은 관점 설명, LinkedIn은 실행 프레임으로 역할을 나눕니다.

결과/교훈: 강한 뷰티 브랜드는 더 예쁘게 포장된 브랜드가 아니라, 더 명확하게 증명되는 브랜드입니다."""

    x = """좋은 뷰티 브랜드는 예쁜 말보다 검증 가능한 가설에서 시작됩니다.

고객의 문제, 제품의 근거, 감각 신호, 브랜드 언어, 채널 행동이 한 구조로 연결될 때 브랜드는 더 명확하게 증명됩니다.

#bbbbbeauty #BeautyBranding"""

    (OUT / "instagram-caption.txt").write_text(instagram, encoding="utf-8")
    (OUT / "facebook-caption.txt").write_text(facebook, encoding="utf-8")
    (OUT / "linkedin-post.txt").write_text(linkedin, encoding="utf-8")
    (OUT / "x-post.txt").write_text(x, encoding="utf-8")
    (OUT / "README.md").write_text(
        "# Beauty Myth Lab\n\n"
        "- Date: 2026-06-19\n"
        "- Direction: Radical Laboratory\n"
        "- Instagram: 6-slide carousel, visual thesis\n"
        "- Facebook: long-form argument, claim plus reasons\n"
        "- LinkedIn: problem-solution-execution-result structure\n"
        "- X: concise thesis with two hashtags\n"
        "- Topic: A beauty brand starts with a testable hypothesis.\n",
        encoding="utf-8",
    )


def main() -> None:
    create_images()
    create_texts()
    print(OUT)


if __name__ == "__main__":
    main()
