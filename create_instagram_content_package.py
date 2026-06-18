from __future__ import annotations

import math
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "artifacts" / "instagram-content-radical-laboratory"
FONT_REGULAR = Path(r"C:\Windows\Fonts\NotoSansKR-VF.ttf")
FONT_BOLD = Path(r"C:\Windows\Fonts\malgunbd.ttf")

BLACK = "#080808"
GRAY = "#687278"
LIGHT = "#d7dcdd"
PAPER = "#ffffff"
WHITE = "#ffffff"
AMBER = "#ff7043"
PALE_AMBER = "#00d6c9"
CYAN = "#00d6c9"
ORANGE = "#ff7043"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REGULAR), size)


def canvas(size: tuple[int, int]) -> Image.Image:
    return Image.new("RGB", size, PAPER)


def lab_grid(draw: ImageDraw.ImageDraw, size: tuple[int, int], dark: bool = False) -> None:
    w, h = size
    color = "#202426" if dark else "#edf0f0"
    for x in range(0, w, 54):
        draw.line((x, 0, x, h), fill=color, width=1)
    for y in range(0, h, 54):
        draw.line((0, y, w, y), fill=color, width=1)
    mark = CYAN if dark else BLACK
    for x, y in ((34, 34), (w - 34, 34), (34, h - 34), (w - 34, h - 34)):
        draw.line((x - 12, y, x + 12, y), fill=mark, width=2)
        draw.line((x, y - 12, x, y + 12), fill=mark, width=2)


def text(
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


def header(draw: ImageDraw.ImageDraw, width: int, index: str = "") -> None:
    draw.rectangle((0, 0, width, 142), fill=BLACK)
    text(draw, (72, 49), "bbbb / LAB", 39, WHITE, bold=True)
    text(draw, (width - 72, 64), index, 25, CYAN, bold=True, anchor="ra")


def footer(draw: ImageDraw.ImageDraw, width: int, label: str) -> None:
    draw.rectangle((0, 1244, width, 1350), fill=BLACK)
    text(draw, (72, 1275), label.upper(), 18, WHITE)
    text(draw, (width - 72, 1275), "BBBB.BEAUTY / 2026", 18, CYAN, bold=True, anchor="ra")


def molecule(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], seed: int = 3) -> None:
    rng = np.random.default_rng(seed)
    x0, y0, x1, y1 = box
    points = [
        (int(rng.uniform(x0, x1)), int(rng.uniform(y0, y1)))
        for _ in range(26)
    ]
    for i, p in enumerate(points):
        distances = sorted(
            ((math.dist(p, q), j, q) for j, q in enumerate(points) if j != i),
            key=lambda item: item[0],
        )
        for _, j, q in distances[:2]:
            if j > i:
                draw.line((*p, *q), fill=CYAN if i % 3 else ORANGE, width=2)
    for i, (x, y) in enumerate(points):
        r = 4 + (i % 4) * 2
        fill = ORANGE if i % 5 == 0 else BLACK
        draw.rectangle((x - r, y - r, x + r, y + r), fill=fill, outline=BLACK, width=2)


def waves(img: Image.Image, box: tuple[int, int, int, int], phase: float = 0.0) -> None:
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    x0, y0, x1, y1 = box
    for line in range(34):
        pts = []
        offset = line * 8
        for x in range(x0, x1 + 1, 9):
            t = (x - x0) / max(1, x1 - x0)
            y = y0 + (y1 - y0) * 0.5
            y += math.sin(t * 7.2 + phase + line * 0.05) * (55 + 65 * t)
            y += offset - 135
            pts.append((x, int(y)))
        alpha = max(20, 105 - line * 2)
        d.line(pts, fill=(0, 214, 201, alpha), width=2)
    glow = overlay.filter(ImageFilter.GaussianBlur(13))
    img.alpha_composite(glow)
    img.alpha_composite(overlay)


def pill(draw: ImageDraw.ImageDraw, xy: tuple[int, int], value: str) -> None:
    x, y = xy
    bbox = draw.textbbox((0, 0), value, font=font(24, True))
    w = bbox[2] - bbox[0] + 40
    draw.rectangle((x, y, x + w, y + 52), fill=BLACK)
    draw.rectangle((x, y, x + 10, y + 52), fill=CYAN)
    text(draw, (x + 25, y + 11), value, 22, WHITE, bold=True)


def save(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(path, quality=95)


def carousel_slide(
    number: int,
    title_value: str,
    body: str,
    accent: str,
    diagram: str,
) -> Image.Image:
    img = canvas((1080, 1350)).convert("RGBA")
    d = ImageDraw.Draw(img)
    lab_grid(d, (1080, 1350))
    header(d, 1080, f"{number:02d} / 06")
    text(d, (1005, 175), f"0{number}", 132, LIGHT, True, "ra")
    pill(d, (72, 183), accent)
    text(d, (72, 282), title_value, 64, bold=True, spacing=18)
    text(d, (72, 485), body, 31, GRAY, spacing=15)

    if diagram == "gap":
        molecule(d, (70, 705, 480, 1120), 7)
        d.rectangle((510, 775, 518, 1115), fill=CYAN)
        text(d, (566, 798), "좋은 기술", 36, bold=True)
        text(d, (566, 866), "복잡한 설명", 36, GRAY)
        text(d, (566, 934), "낮은 이해", 36, GRAY)
        text(d, (566, 1002), "선택의 지연", 36, fill=ORANGE, bold=True)
    elif diagram == "formula":
        boxes = [("SCIENCE", 72), ("MESSAGE", 390), ("EXPERIENCE", 708)]
        for label, x in boxes:
            d.rectangle((x, 770, x + 260, 950), fill=WHITE, outline=BLACK, width=4)
            text(d, (x + 130, 860), label, 25, bold=True, anchor="mm")
        d.line((332, 860, 382, 860), fill=ORANGE, width=8)
        d.line((650, 860, 700, 860), fill=CYAN, width=8)
        waves(img, (410, 940, 1030, 1170), 0.5)
    elif diagram == "layers":
        labels = ["성분", "작용 원리", "임상 데이터", "고객 언어"]
        for i, label in enumerate(labels):
            y = 720 + i * 105
            fill = CYAN if i == 3 else WHITE
            d.rectangle((110 + i * 28, y, 900 - i * 28, y + 72), fill=fill, outline=BLACK, width=2)
            text(d, (505, y + 36), label, 28, BLACK, bold=i == 3, anchor="mm")
    elif diagram == "visible":
        molecule(d, (65, 690, 515, 1135), 11)
        waves(img, (455, 720, 1040, 1135), 1.2)
        text(d, (540, 1075), "보이지 않는 원리를\n이해 가능한 장면으로", 29, bold=True)
    elif diagram == "channels":
        labels = ["출시", "교육", "영업", "전시", "SNS"]
        center = (540, 890)
        d.ellipse((450, 800, 630, 980), fill=BLACK)
        text(d, center, "ONE\nSTORY", 26, WHITE, True, "mm")
        for i, label in enumerate(labels):
            a = -math.pi / 2 + i * 2 * math.pi / len(labels)
            x = int(center[0] + math.cos(a) * 310)
            y = int(center[1] + math.sin(a) * 230)
            d.line((*center, x, y), fill=LIGHT, width=3)
            d.rectangle((x - 64, y - 42, x + 64, y + 42), fill=WHITE, outline=BLACK, width=2)
            text(d, (x, y), label, 25, bold=True, anchor="mm")
    elif diagram == "cta":
        d.rectangle((72, 735, 1008, 1090), fill=BLACK)
        d.rectangle((72, 735, 90, 1090), fill=ORANGE)
        text(d, (120, 800), "PROJECT CHECK", 24, CYAN, True)
        text(d, (120, 862), "무엇을 설명해야 하나요?", 34, WHITE, True)
        text(d, (120, 924), "누가 이해해야 하나요?", 34, WHITE, True)
        text(d, (120, 986), "어디에서 활용하나요?", 34, WHITE, True)

    footer(d, 1080, "Science to Message, Beauty to Experience.")
    return img


def create_carousel() -> None:
    slides = [
        ("기술이 좋아도\n이해하기 어렵다면?", "고객은 기술의 우수성보다\n이해할 수 있는 차이를 먼저 선택합니다.", "THE UNDERSTANDING GAP", "gap"),
        ("좋은 기술과\n선택 사이의 거리", "성분, 메커니즘, 임상 데이터가\n전문 언어에 머물면 신뢰로 이어지기 어렵습니다.", "WHY IT MATTERS", "layers"),
        ("과학을 메시지로", "핵심 원리를 잃지 않으면서\n고객이 기억할 수 있는 언어로 바꿉니다.", "SCIENCE TO MESSAGE", "formula"),
        ("보이지 않는 것을\n보이게 합니다", "3D와 MOA 시각화는 복잡한 작용 원리를\n직관적인 장면과 흐름으로 전환합니다.", "MEDICAL VISUALIZATION", "visible"),
        ("하나의 기술 이야기,\n여러 개의 접점", "출시부터 교육, 영업, 전시, SNS까지\n일관된 브랜드 자산으로 확장합니다.", "CONTENT EXPANSION", "channels"),
        ("브랜드의 기술을\n어떻게 보여주고 있나요?", "설명이 필요한 기술이 있다면\n제품, 대상, 활용 채널을 알려주세요.", "START A PROJECT", "cta"),
    ]
    folder = OUT / "01-carousel-understanding-gap"
    for i, args in enumerate(slides, 1):
        save(carousel_slide(i, *args), folder / f"{i:02d}.png")


def story_base(index: str, label: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = canvas((1080, 1920)).convert("RGBA")
    d = ImageDraw.Draw(img)
    lab_grid(d, (1080, 1920))
    d.rectangle((0, 0, 1080, 164), fill=BLACK)
    text(d, (72, 58), "bbbb / LAB", 39, WHITE, bold=True)
    text(d, (1008, 73), index, 25, CYAN, bold=True, anchor="ra")
    text(d, (1000, 185), index.split()[0], 145, LIGHT, True, "ra")
    pill(d, (72, 210), label)
    return img, d


def story_footer(d: ImageDraw.ImageDraw, value: str = "@bbbb.beauty_official") -> None:
    d.rectangle((0, 1770, 1080, 1920), fill=BLACK)
    text(d, (72, 1817), value, 22, WHITE)
    text(d, (1008, 1817), "RADICAL LABORATORY", 19, CYAN, True, "ra")


def create_story_carousel() -> None:
    folder = OUT / "03-story-carousel-needs"
    specs = [
        ("01 / 05", "PROJECT QUESTION", "기술을 설명하기\n어려우신가요?", "복잡한 내용을 고객의 언어로 바꾸는 것부터\n콘텐츠 제작은 시작됩니다.", "question"),
        ("02 / 05", "POLL", "지금 가장 필요한\n콘텐츠는 무엇인가요?", "A  제품 출시\nB  고객 교육", "poll"),
        ("03 / 05", "POLL", "어디에서\n활용할 예정인가요?", "A  영업 자료\nB  전시 콘텐츠", "poll"),
        ("04 / 05", "CHOOSE", "어떤 방식이\n더 필요한가요?", "A  3D 이미지\nB  MOA 애니메이션", "poll"),
        ("05 / 05", "DM US", "프로젝트를\n알려주세요", "제품 · 일정 · 대상 · 활용 채널\n네 가지만 보내주시면 됩니다.", "dm"),
    ]
    for i, (idx, label, title_value, body, mode) in enumerate(specs, 1):
        img, d = story_base(idx, label)
        text(d, (72, 380), title_value, 70, bold=True, spacing=22)
        text(d, (72, 650), body, 34, GRAY, spacing=22)
        if mode == "question":
            molecule(d, (95, 950, 895, 1530), 9)
            d.rectangle((140, 1450, 940, 1580), fill=BLACK)
            d.rectangle((140, 1450, 156, 1580), fill=ORANGE)
            text(d, (540, 1515), "질문 스티커 영역", 28, WHITE, anchor="mm")
        elif mode == "poll":
            values = body.split("\n")
            for j, value in enumerate(values):
                y = 1050 + j * 145
                d.rectangle((110, y, 970, y + 105), fill=WHITE, outline=BLACK, width=4)
                d.rectangle((110, y, 127, y + 105), fill=CYAN if j == 0 else ORANGE)
                text(d, (540, y + 52), value, 30, bold=True, anchor="mm")
            text(d, (540, 1415), "Instagram 투표 스티커 추가", 25, GRAY, anchor="mm")
        else:
            d.rectangle((110, 1040, 970, 1375), fill=BLACK)
            d.rectangle((110, 1040, 128, 1375), fill=ORANGE)
            text(d, (160, 1100), "DM CHECKLIST", 24, CYAN, True)
            text(d, (160, 1170), "1. 제품 또는 기술\n2. 목표 일정\n3. 주요 대상\n4. 활용 채널", 34, WHITE, True, spacing=21)
            d.rectangle((250, 1480, 830, 1585), fill=CYAN)
            text(d, (540, 1532), "메시지 보내기", 30, bold=True, anchor="mm")
        story_footer(d)
        save(img, folder / f"{i:02d}.png")


def create_contact_stories() -> None:
    folder = OUT / "05-story-contact"
    specs = [
        ("01 / 04", "제품 출시를\n준비하고 계신가요?", "과학적 정보와 브랜드 경험을\n하나의 콘텐츠로 연결합니다.", "hero"),
        ("02 / 04", "필요한 콘텐츠를\n선택하세요", "3D VISUAL\nMOA ANIMATION\nEDUCATION\nEXHIBITION", "services"),
        ("03 / 04", "프로젝트는\n이렇게 진행됩니다", "상담  →  기획  →  제작  →  납품", "process"),
        ("04 / 04", "프로젝트 내용을\nDM으로 보내주세요", "제품 · 일정 · 필요 콘텐츠", "cta"),
    ]
    for i, (idx, title_value, body, mode) in enumerate(specs, 1):
        img, d = story_base(idx, "PROJECT INQUIRY")
        text(d, (72, 395), title_value, 69, bold=True, spacing=22)
        text(d, (72, 680), body, 34, GRAY, spacing=21)
        if mode == "hero":
            molecule(d, (50, 950, 520, 1540), 15)
            waves(img, (360, 970, 1080, 1600), 0.4)
        elif mode == "services":
            for j, value in enumerate(body.split("\n")):
                y = 980 + j * 135
                d.rectangle((110, y, 970, y + 92), fill=BLACK if j % 2 == 0 else WHITE, outline=BLACK, width=3)
                text(d, (160, y + 46), value, 29, bold=True, anchor="lm")
                if j % 2 == 0:
                    text(d, (160, y + 46), value, 29, WHITE, bold=True, anchor="lm")
                text(d, (915, y + 46), "→", 30, CYAN if j % 2 == 0 else ORANGE, bold=True, anchor="rm")
        elif mode == "process":
            labels = ["상담", "기획", "제작", "납품"]
            for j, value in enumerate(labels):
                x = 140 + j * 250
                d.rectangle((x - 57, 1120, x + 57, 1234), fill=BLACK if j == 0 else WHITE, outline=BLACK, width=3)
                text(d, (x, 1177), value, 26, WHITE if j == 0 else BLACK, True, "mm")
                if j < 3:
                    d.line((x + 58, 1177, x + 190, 1177), fill=CYAN if j % 2 == 0 else ORANGE, width=7)
        else:
            d.rectangle((130, 1060, 950, 1410), fill=BLACK)
            d.rectangle((130, 1060, 150, 1410), fill=ORANGE)
            text(d, (540, 1135), "현재 준비 중인 프로젝트를\n알려주세요.", 38, WHITE, True, "ma", 20)
            d.rectangle((260, 1510, 820, 1615), fill=CYAN)
            text(d, (540, 1562), "질문 스티커 추가", 29, bold=True, anchor="mm")
        story_footer(d, "CONTACT · @bbbb.beauty_official")
        save(img, folder / f"{i:02d}.png")


def reel_frame(
    index: int,
    total: int,
    kicker: str,
    title_value: str,
    body: str,
    visual: str,
    phase: float = 0.0,
) -> Image.Image:
    img, d = story_base(f"{index:02d} / {total:02d}", kicker)
    text(d, (72, 420), title_value, 71, bold=True, spacing=22)
    text(d, (72, 695), body, 34, GRAY, spacing=18)
    if visual == "science":
        molecule(d, (35, 1020, 720, 1600), index + 4)
    elif visual == "message":
        molecule(d, (35, 1040, 450, 1530), index + 6)
        waves(img, (360, 1050, 1080, 1600), phase)
    elif visual == "experience":
        waves(img, (0, 980, 1080, 1630), phase)
    elif visual == "process":
        stages = ["RESEARCH", "SCRIPT", "STORYBOARD", "ANIMATIC", "3D · MOTION", "FINAL"]
        for j, stage in enumerate(stages):
            y = 930 + j * 112
            active = j == index - 1
            d.rectangle((120, y, 960, y + 78), fill=BLACK if active else WHITE, outline=BLACK, width=2)
            if active:
                d.rectangle((120, y, 138, y + 78), fill=ORANGE)
            text(d, (170, y + 39), f"{j + 1:02d}", 23, CYAN if active else GRAY, True, "lm")
            text(d, (260, y + 39), stage, 26, WHITE if active else BLACK, True, "lm")
    story_footer(d)
    return img


def zoom_frame(img: Image.Image, progress: float) -> np.ndarray:
    rgb = img.convert("RGB")
    w, h = rgb.size
    scale = 1.0 + progress * 0.025
    nw, nh = int(w * scale), int(h * scale)
    enlarged = rgb.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - w) // 2
    top = (nh - h) // 2
    return np.asarray(enlarged.crop((left, top, left + w, top + h)))


def write_video(frames: list[Image.Image], path: Path, seconds_each: float = 3.0) -> None:
    fps = 24
    path.parent.mkdir(parents=True, exist_ok=True)
    writer = imageio_ffmpeg.write_frames(
        str(path),
        (1080, 1920),
        fps=fps,
        codec="libx264",
        pix_fmt_out="yuv420p",
        macro_block_size=1,
        output_params=["-movflags", "+faststart", "-crf", "19"],
    )
    writer.send(None)
    try:
        count = int(seconds_each * fps)
        for source in frames:
            for n in range(count):
                writer.send(zoom_frame(source, n / max(1, count - 1)).tobytes())
    finally:
        writer.close()


def create_brand_reel() -> None:
    folder = OUT / "02-reel-brand-philosophy"
    frames = [
        reel_frame(1, 5, "SCIENCE", "복잡한 과학은", "정확하지만\n고객에게는 어렵게 느껴질 수 있습니다.", "science"),
        reel_frame(2, 5, "TRANSLATION", "핵심을 발견하고", "성분, 메커니즘, 데이터를\n하나의 명확한 이야기로 정리합니다.", "science"),
        reel_frame(3, 5, "MESSAGE", "이해 가능한\n메시지로", "과학적 정확성을 유지하며\n고객이 기억할 수 있는 언어로 전환합니다.", "message", 0.4),
        reel_frame(4, 5, "EXPERIENCE", "감각적인\n경험으로", "3D, MOA, 모션을 통해\n보이지 않는 원리를 장면으로 만듭니다.", "experience", 1.0),
        reel_frame(5, 5, "BBBB.BEAUTY", "Science to Message,\nBeauty to Experience.", "과학을 메시지로,\n아름다움을 경험으로.", "experience", 1.8),
    ]
    for i, frame in enumerate(frames, 1):
        save(frame, folder / "frames" / f"{i:02d}.png")
    write_video(frames, folder / "brand-philosophy-reel.mp4", 3.2)


def create_moa_reel() -> None:
    folder = OUT / "04-reel-moa-process"
    titles = [
        ("RESEARCH", "자료 조사", "논문과 제품 정보를 분석해\n정확한 출발점을 만듭니다."),
        ("SCRIPT", "시나리오", "전달 대상과 목적에 맞춰\n핵심 메시지의 순서를 설계합니다."),
        ("STORYBOARD", "스토리보드", "장면, 정보, 카메라 흐름을\n제작 전에 검토합니다."),
        ("ANIMATIC", "애니매틱", "타이밍과 전환을 확인해\n수정 비용을 줄입니다."),
        ("3D · MOTION", "3D · 모션 제작", "분자 구조와 작용 원리를\n직관적인 움직임으로 구현합니다."),
        ("FINAL", "최종 콘텐츠", "출시, 교육, 영업, 전시에\n활용 가능한 브랜드 자산으로 완성합니다."),
    ]
    frames = [
        reel_frame(i, 6, kicker, title_value, body, "process")
        for i, (kicker, title_value, body) in enumerate(titles, 1)
    ]
    for i, frame in enumerate(frames, 1):
        save(frame, folder / "frames" / f"{i:02d}.png")
    write_video(frames, folder / "moa-production-process-reel.mp4", 3.6)


def create_manifest() -> None:
    value = """# Instagram Content Package

Created: 2026-06-15
Brand: bbbb.beauty

## Deliverables

1. `01-carousel-understanding-gap/`
   - 6 PNG slides, 1080 x 1350
2. `02-reel-brand-philosophy/`
   - 5 source frames, 1080 x 1920
   - `brand-philosophy-reel.mp4`
3. `03-story-carousel-needs/`
   - 5 PNG story frames, 1080 x 1920
   - Add native Instagram poll/question stickers at upload time.
4. `04-reel-moa-process/`
   - 6 source frames, 1080 x 1920
   - `moa-production-process-reel.mp4`
5. `05-story-contact/`
   - 4 PNG story frames, 1080 x 1920
   - Add native Instagram question sticker at upload time.

## Visual System

- Direction: Radical Laboratory
- Background: pure white and absolute black
- Typography: large technical sans serif
- Accent: Signal Cyan `#00D6C9` and Electric Orange `#FF7043`
- Graphics: laboratory grid, coordinates, data labels, square modules
- Main line: Science to Message, Beauty to Experience.
"""
    (OUT / "README.md").write_text(value, encoding="utf-8")


def main() -> None:
    create_carousel()
    create_brand_reel()
    create_story_carousel()
    create_moa_reel()
    create_contact_stories()
    create_manifest()
    print(OUT)


if __name__ == "__main__":
    main()
