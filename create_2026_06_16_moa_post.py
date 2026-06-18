from __future__ import annotations

import math
import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "artifacts" / "2026-06-16-moa-visualization"


def first_existing(paths: list[str]) -> Path:
    for raw in paths:
        if not raw:
            continue
        path = Path(raw)
        if path.is_file():
            return path
    raise FileNotFoundError(
        "No usable Korean font found. Install fonts-noto-cjk or set "
        "FONT_REGULAR/FONT_BOLD."
    )


FONT_REGULAR = first_existing(
    [
        os.getenv("FONT_REGULAR", ""),
        r"C:\Windows\Fonts\NotoSansKR-VF.ttf",
        r"C:\Windows\Fonts\malgun.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansKR-Regular.otf",
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
        "/usr/share/fonts/truetype/noto/NotoSansKR-Bold.otf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
)

WHITE = "#ffffff"
BLACK = "#080808"
CYAN = "#00d6c9"
ORANGE = "#ff7043"
STEEL = "#687278"
GRID = "#edf0f0"
LIGHT = "#d7dcdd"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REGULAR), size)


def text(draw: ImageDraw.ImageDraw, xy, value: str, size: int, fill=BLACK, bold=False, anchor=None, spacing=12):
    draw.multiline_text(xy, value, font=font(size, bold), fill=fill, anchor=anchor, spacing=spacing)


def lab_grid(draw: ImageDraw.ImageDraw, w: int, h: int) -> None:
    for x in range(0, w, 54):
        draw.line((x, 0, x, h), fill=GRID, width=1)
    for y in range(0, h, 54):
        draw.line((0, y, w, y), fill=GRID, width=1)


def header(draw: ImageDraw.ImageDraw, page: int, total: int) -> None:
    draw.rectangle((0, 0, 1080, 142), fill=BLACK)
    text(draw, (72, 49), "bbbb / LAB", 39, WHITE, True)
    text(draw, (1008, 64), f"{page:02d} / {total:02d}", 25, CYAN, True, "ra")


def footer(draw: ImageDraw.ImageDraw) -> None:
    draw.rectangle((0, 1244, 1080, 1350), fill=BLACK)
    text(draw, (72, 1275), "MAKING INVISIBLE SCIENCE VISIBLE", 18, WHITE)
    text(draw, (1008, 1275), "BBBB.BEAUTY / 2026", 18, CYAN, True, "ra")


def label(draw: ImageDraw.ImageDraw, value: str, x=72, y=183) -> None:
    bbox = draw.textbbox((0, 0), value, font=font(22, True))
    w = bbox[2] - bbox[0] + 50
    draw.rectangle((x, y, x + w, y + 52), fill=BLACK)
    draw.rectangle((x, y, x + 10, y + 52), fill=CYAN)
    text(draw, (x + 25, y + 11), value, 22, WHITE, True)


def molecule(draw: ImageDraw.ImageDraw, box, seed=1) -> None:
    rng = np.random.default_rng(seed)
    x0, y0, x1, y1 = box
    pts = [(int(rng.uniform(x0, x1)), int(rng.uniform(y0, y1))) for _ in range(22)]
    for i, p in enumerate(pts):
        links = sorted(((math.dist(p, q), q) for q in pts if q != p), key=lambda v: v[0])[:2]
        for _, q in links:
            draw.line((*p, *q), fill=CYAN if i % 2 else ORANGE, width=2)
    for i, (x, y) in enumerate(pts):
        r = 6 if i % 5 else 10
        draw.rectangle((x - r, y - r, x + r, y + r), fill=BLACK if i % 5 else ORANGE)


def flow(draw: ImageDraw.ImageDraw, y: int, labels: list[str]) -> None:
    x = 110
    box_w = 170
    step = 230
    for i, value in enumerate(labels):
        draw.rectangle((x, y, x + box_w, y + 104), fill=BLACK if i == 1 else WHITE, outline=BLACK, width=4)
        text(draw, (x + box_w // 2, y + 52), value, 26, WHITE if i == 1 else BLACK, True, "mm")
        if i < len(labels) - 1:
            draw.line((x + box_w, y + 52, x + step, y + 52), fill=CYAN if i % 2 else ORANGE, width=7)
        x += step


def stage_list(draw: ImageDraw.ImageDraw, active: int) -> None:
    stages = ["STRUCTURE", "SEQUENCE", "MESSAGE", "APPLICATION"]
    for i, stage in enumerate(stages, 1):
        y = 750 + (i - 1) * 110
        is_active = i == active
        draw.rectangle((120, y, 960, y + 82), fill=BLACK if is_active else WHITE, outline=BLACK, width=3)
        if is_active:
            draw.rectangle((120, y, 140, y + 82), fill=ORANGE)
        text(draw, (175, y + 41), f"{i:02d}", 24, CYAN if is_active else STEEL, True, "lm")
        text(draw, (275, y + 41), stage, 28, WHITE if is_active else BLACK, True, "lm")


def make_slide(page: int, kicker: str, title: str, body: str, mode: str) -> Image.Image:
    img = Image.new("RGB", (1080, 1350), WHITE)
    d = ImageDraw.Draw(img)
    lab_grid(d, 1080, 1350)
    header(d, page, 6)
    label(d, kicker)
    text(d, (1005, 175), f"{page:02d}", 132, LIGHT, True, "ra")
    text(d, (72, 300), title, 64, BLACK, True, spacing=20)
    text(d, (72, 505), body, 31, STEEL, False, spacing=16)

    if mode == "cover":
        molecule(d, (95, 720, 985, 1110), 16)
        draw_box = (72, 1045, 1008, 1135)
        d.rectangle(draw_box, fill=BLACK)
        d.rectangle((72, 1045, 92, 1135), fill=ORANGE)
        text(d, (120, 1089), "MOA = MECHANISM OF ACTION", 27, WHITE, True, "lm")
    elif mode == "structure":
        molecule(d, (120, 710, 555, 1110), 22)
        d.rectangle((610, 765, 955, 1070), fill=BLACK)
        text(d, (650, 815), "무엇이\n어디에서\n작동하는가", 40, WHITE, True, spacing=18)
        text(d, (650, 1010), "STRUCTURE", 24, CYAN, True)
    elif mode == "sequence":
        flow(d, 830, ["진입", "작용", "변화", "결과"])
        text(d, (110, 1010), "순서가 없으면 고객은 원리를 기억하지 못합니다.", 29, STEEL)
    elif mode == "message":
        stage_list(d, 3)
        d.rectangle((120, 1190, 960, 1230), fill=CYAN)
    elif mode == "application":
        labels = ["LAUNCH", "EDUCATION", "SALES", "EXHIBITION", "SOCIAL"]
        for i, item in enumerate(labels):
            y = 720 + i * 86
            d.rectangle((150, y, 930, y + 60), fill=BLACK if i % 2 == 0 else WHITE, outline=BLACK, width=2)
            text(d, (190, y + 30), item, 26, WHITE if i % 2 == 0 else BLACK, True, "lm")
            text(d, (890, y + 30), "→", 28, CYAN if i % 2 == 0 else ORANGE, True, "rm")
    elif mode == "cta":
        d.rectangle((110, 760, 970, 1060), fill=BLACK)
        d.rectangle((110, 760, 132, 1060), fill=ORANGE)
        text(d, (165, 825), "PROJECT CHECK", 25, CYAN, True)
        text(d, (165, 890), "제품 · 기술 · 대상 · 활용 채널", 38, WHITE, True)
        d.rectangle((250, 1110, 830, 1195), fill=CYAN)
        text(d, (540, 1152), "DM으로 문의", 30, BLACK, True, "mm")

    footer(d)
    return img


def main() -> None:
    slides = [
        ("MOA VISUALIZATION", "MOA 애니메이션은\n무엇을 전달해야 할까요?", "보이지 않는 작용 원리를\n고객이 이해할 수 있는 흐름으로 바꿉니다.", "cover"),
        ("01 STRUCTURE", "첫 번째는\n구조입니다", "성분, 세포, 수용체, 피부층처럼\n작용이 일어나는 위치를 먼저 보여줘야 합니다.", "structure"),
        ("02 SEQUENCE", "두 번째는\n작용 순서입니다", "좋은 MOA는 장면이 아니라\n원인이 결과로 이어지는 순서를 설계합니다.", "sequence"),
        ("03 MESSAGE", "세 번째는\n기억될 메시지입니다", "과학적 정확성만으로는 부족합니다.\n고객이 기억할 한 문장까지 정리해야 합니다.", "message"),
        ("04 APPLICATION", "하나의 MOA는\n여러 채널로 확장됩니다", "출시, 교육, 영업, 전시, SNS까지\n같은 기술 이야기를 일관되게 활용합니다.", "application"),
        ("PROJECT INQUIRY", "보이지 않는 기술을\n보이게 만들 준비가 됐나요?", "제품 정보와 활용 채널을 보내주시면\n콘텐츠 구조부터 제안드립니다.", "cta"),
    ]
    folder = OUT / "carousel"
    folder.mkdir(parents=True, exist_ok=True)
    for i, args in enumerate(slides, 1):
        make_slide(i, *args).save(folder / f"{i:02d}.png", quality=95)

    instagram_caption = """MOA 애니메이션은 단순히 멋진 3D 장면을 만드는 일이 아닙니다.

고객이 작용 원리를 이해하려면 세 가지가 필요합니다.

1. 어디에서 작동하는가
2. 어떤 순서로 변화가 일어나는가
3. 결국 어떤 메시지를 기억해야 하는가

bbbb.beauty는 복잡한 메디컬·바이오·뷰티 기술을 이해 가능한 시각적 경험으로 전환합니다.

#bbbbbeauty #MOAAnimation #MedicalVisualization #3DAnimation #뷰티마케팅"""

    facebook_caption = """MOA 애니메이션은 단순히 멋진 3D 장면을 만드는 작업이 아닙니다.

브랜드의 기술이 고객에게 이해되려면 구조, 작용 순서, 기억될 메시지가 함께 설계되어야 합니다.

성분이 어디에서 작동하는지, 어떤 순서로 변화가 일어나는지, 고객이 마지막에 어떤 차이를 기억해야 하는지를 명확히 보여줄 때 기술 콘텐츠는 제품 출시, 교육, 영업과 전시에서 반복 활용할 수 있는 브랜드 자산이 됩니다.

bbbb.beauty는 복잡한 메디컬·바이오·뷰티 기술을 이해 가능한 시각적 경험으로 전환합니다.

#bbbbbeauty #MOAAnimation #MedicalVisualization #메디컬콘텐츠"""

    (OUT / "instagram-caption.txt").write_text(instagram_caption, encoding="utf-8")
    (OUT / "facebook-caption.txt").write_text(facebook_caption, encoding="utf-8")
    (OUT / "README.md").write_text(
        "# 2026-06-16 MOA Visualization Post\n\n"
        "Topic: MOA animation must communicate structure, sequence, and message.\n"
        "Design: Radical Laboratory\n"
        "Format: 6-slide carousel, 1080 x 1350\n",
        encoding="utf-8",
    )
    print(OUT)


if __name__ == "__main__":
    main()
