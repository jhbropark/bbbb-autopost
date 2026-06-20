from __future__ import annotations

from pathlib import Path
import os

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
ASSET = ROOT / "social" / "2026-06-20-evidence-note" / "hero-v1.png"
OUT = ROOT / "artifacts" / "2026-06-20-evidence-note"

IVORY = "#F4F0E8"
BLACK = "#101214"
WHITE = "#FFFDF9"
MUTED = "#71777D"
LIME = "#D8FF00"
CYAN = "#00D7D2"


def first_font(paths: list[str]) -> Path:
    for raw in paths:
        if raw and Path(raw).is_file():
            return Path(raw)
    raise FileNotFoundError("No usable Korean font found.")


REGULAR = first_font([os.getenv("FONT_REGULAR", ""), r"C:\Windows\Fonts\NotoSansKR-VF.ttf", r"C:\Windows\Fonts\malgun.ttf"])
BOLD = first_font([os.getenv("FONT_BOLD", ""), r"C:\Windows\Fonts\malgunbd.ttf", r"C:\Windows\Fonts\NotoSansKR-VF.ttf"])


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(BOLD if bold else REGULAR), size)


def write(draw: ImageDraw.ImageDraw, xy: tuple[int, int], value: str, size: int, fill: str, bold: bool = False, spacing: int = 10) -> None:
    draw.multiline_text(xy, value, font=font(size, bold), fill=fill, spacing=spacing)


def cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    width, height = size
    scale = max(width / image.width, height / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - width) // 2
    top = (resized.height - height) // 2
    return resized.crop((left, top, left + width, top + height))


def chrome(draw: ImageDraw.ImageDraw, number: str) -> None:
    draw.rectangle((0, 0, 1080, 92), fill=BLACK)
    write(draw, (64, 29), "bbbb / RADICAL LABORATORY", 21, WHITE, True)
    write(draw, (914, 29), number, 21, CYAN, True)


def footer(draw: ImageDraw.ImageDraw) -> None:
    write(draw, (64, 1008), "EVIDENCE NOTE 01", 18, MUTED, True)


def slide_one(hero: Image.Image) -> Image.Image:
    canvas = cover(hero, (1080, 1080))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, 1080, 92), fill=BLACK)
    write(draw, (64, 29), "bbbb / RADICAL LABORATORY", 21, WHITE, True)
    write(draw, (914, 29), "01 / 05", 21, CYAN, True)
    draw.rectangle((0, 700, 1080, 1080), fill=BLACK)
    draw.rectangle((64, 742, 250, 782), fill=LIME)
    write(draw, (84, 752), "SOURCE BRIEF", 17, BLACK, True)
    write(draw, (64, 820), "좋은 뷰티 브랜드는\n성분보다 먼저\n검증 구조를 설계합니다.", 54, WHITE, True, 6)
    return canvas


def slide_question(hero: Image.Image, number: str, eyebrow: str, headline: str, note: str, crop_top: int) -> Image.Image:
    canvas = Image.new("RGB", (1080, 1080), IVORY)
    canvas.paste(cover(hero, (1080, 350)), (0, 92 - crop_top))
    draw = ImageDraw.Draw(canvas)
    chrome(draw, number)
    draw.rectangle((64, 495, 264, 535), fill=BLACK)
    write(draw, (84, 505), eyebrow, 17, WHITE, True)
    write(draw, (64, 584), headline, 51, BLACK, True, 8)
    write(draw, (64, 820), note, 28, MUTED, False, 8)
    footer(draw)
    return canvas


def slide_five() -> Image.Image:
    canvas = Image.new("RGB", (1080, 1080), BLACK)
    draw = ImageDraw.Draw(canvas)
    write(draw, (64, 66), "bbbb / RADICAL LABORATORY", 21, WHITE, True)
    write(draw, (914, 66), "05 / 05", 21, CYAN, True)
    draw.rectangle((64, 192, 306, 234), fill=LIME)
    write(draw, (84, 202), "SAVE THIS", 18, BLACK, True)
    write(draw, (64, 302), "저장할 기준", 34, WHITE, True)
    write(draw, (64, 392), "제품 · 고객 · 증거 · 감각\n네 요소가 하나의 설명으로\n연결되는가?", 52, WHITE, True, 10)
    draw.line((64, 744, 1016, 744), fill="#44484B", width=2)
    write(draw, (64, 792), "다음 제품 리뷰에서 이 질문부터 확인해보세요.", 27, "#BCC1C5")
    write(draw, (64, 1008), "EVIDENCE NOTE 01", 18, CYAN, True)
    return canvas


def story() -> Image.Image:
    canvas = Image.new("RGB", (1080, 1920), BLACK)
    draw = ImageDraw.Draw(canvas)
    write(draw, (64, 82), "bbbb / RADICAL LABORATORY", 22, WHITE, True)
    write(draw, (64, 254), "제품 신뢰는\n어디서 시작되나요?", 72, WHITE, True, 12)
    choices = ["A. 성분", "B. 사용 장면", "C. 검증 근거", "D. 브랜드 언어"]
    for index, choice in enumerate(choices):
        y = 742 + index * 166
        draw.rounded_rectangle((64, y, 1016, y + 118), radius=26, outline=CYAN if index == 2 else "#555B60", width=3)
        write(draw, (98, y + 34), choice, 31, WHITE, True)
    write(draw, (64, 1642), "답은 하나가 아닙니다.\n선택의 순간에 서로 연결되어야 합니다.", 31, "#BCC1C5", False, 10)
    write(draw, (64, 1816), "STORY / EVIDENCE CHECK", 19, CYAN, True)
    return canvas


def main() -> None:
    if not ASSET.is_file():
        raise FileNotFoundError(f"Missing hero asset: {ASSET}")
    OUT.mkdir(parents=True, exist_ok=True)
    carousel = OUT / "carousel"
    carousel.mkdir(exist_ok=True)
    hero = Image.open(ASSET).convert("RGB")
    slides = [
        slide_one(hero),
        slide_question(hero, "02 / 05", "QUESTION 01", "이 제품은 어떤 선택을\n더 쉽게 만드나?", "특징만 나열하면 제품은 비교 대상이 됩니다.\n선택의 이유부터 설계해야 합니다.", 0),
        slide_question(hero, "03 / 05", "QUESTION 02", "고객은 무엇을 보고\n믿어도 된다고 판단하나?", "신뢰는 한 문장이 아니라\n제품, 사용 장면, 근거의 연결에서 생깁니다.", 46),
        slide_question(hero, "04 / 05", "QUESTION 03", "감각은 어떤 증거를\n더 선명하게 만드나?", "패키지와 이미지의 역할은 장식이 아닙니다.\n검증 가능한 약속을 기억하게 해야 합니다.", 92),
        slide_five(),
    ]
    for index, slide in enumerate(slides, start=1):
        slide.save(carousel / f"{index:02d}.png", quality=95)
    story().save(OUT / "story-evidence-check.png", quality=95)
    (OUT / "instagram-caption.txt").write_text(
        "좋은 뷰티 브랜드는 성분을 많이 말하기 전에, 고객이 무엇을 보고 믿어도 되는지 설계합니다.\n\n제품, 고객, 증거, 감각. 이 네 요소가 하나의 설명으로 연결될 때 선택의 이유가 생깁니다.\n\n저장해 두고 다음 제품 리뷰에서 확인해보세요.",
        encoding="utf-8",
    )
    (OUT / "README.md").write_text(
        "# Evidence Note 01\n\n- Format: 5-slide Instagram carousel + Story question card\n- Purpose: Source Brief test based on editorial-photo and evidence-first study\n- Theme: A beauty brand begins with a verifiable decision structure\n",
        encoding="utf-8",
    )
    print(OUT)


if __name__ == "__main__":
    main()
