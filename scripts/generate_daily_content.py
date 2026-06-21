#!/usr/bin/env python3
"""Generate a date-specific bbbb.beauty social package for the daily workflow."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ANCHOR_DATE = date(2026, 6, 22)
BLACK = "#101214"
IVORY = "#F4F0E8"
WHITE = "#FFFDF9"
MUTED = "#697177"
CYAN = "#00D7D2"
LIME = "#D8FF00"


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
        "future-city",
        "Future City",
        "SPATIAL EXPERIENCE",
        "좋은 공간은\n3초의 멈춤을\n설계합니다.",
        (
            "사람은 어디에서\n멈추는가?",
            "그 순간 무엇을\n발견하는가?",
            "다음 행동은 어떻게\n이어지는가?",
        ),
        "공간 경험은 장식이 아니라 선택의 흐름입니다.\n\n사람이 멈추는 3초, 발견하는 정보, 다음 행동까지 설계될 때 브랜드는 기억됩니다.",
        "좋은 공간은 눈길을 끄는 오브젝트만으로 완성되지 않습니다. 사람의 흐름이 어디에서 멈추고, 무엇을 발견하며, 어떤 행동으로 이어지는지까지 설계해야 합니다.\n\nBBBB는 공간을 브랜드 메시지가 실제 행동으로 번역되는 장면으로 봅니다.\n\n출처: bbbb.beauty Future City 운영 프레임",
        "문제:\n공간을 보기 좋게 만드는 일과 브랜드 선택을 돕는 경험을 만드는 일은 다릅니다.\n\n해결:\n공간 경험을 멈춤, 발견, 다음 행동의 흐름으로 나누어 설계합니다.\n\n실행:\n1. 사람은 어디에서 멈추는가\n2. 그 순간 무엇을 발견하는가\n3. 다음 행동은 어떻게 이어지는가\n\n이 세 질문은 특정 프로젝트 성과가 아니라, 공간 경험을 설계하기 위한 일반 프레임입니다.",
        "좋은 공간은 장식보다 사람의 다음 행동을 먼저 설계합니다.",
    ),
    Topic(
        "content-business",
        "Content Business",
        "CONTENT SYSTEM",
        "좋은 콘텐츠는\n한 번의 조회보다\n다음 질문을 만듭니다.",
        ("무엇을 기억하게\n만드는가?", "어떤 근거를\n남기는가?", "다음 행동은\n무엇인가?"),
        "좋은 콘텐츠는 한 번의 조회보다 다음 질문을 만듭니다. 기억, 근거, 다음 행동의 흐름을 설계해보세요.",
        "콘텐츠의 역할은 정보를 더하는 데 있지 않습니다. 고객이 무엇을 기억하고, 어떤 근거를 남기며, 다음에 무엇을 하게 할지 정리하는 데 있습니다.\n\n출처: bbbb.beauty Content Business 운영 프레임",
        "문제:\n콘텐츠가 많아도 고객의 다음 행동이 바뀌지 않는 경우가 많습니다.\n\n해결:\n기억, 근거, 다음 행동의 순서를 먼저 설계합니다.\n\n실행:\n각 콘텐츠에서 하나의 질문만 남기고, 그 질문에 답할 근거와 다음 행동을 연결합니다.",
        "콘텐츠의 성과는 조회 수보다 다음 행동에서 드러납니다.",
    ),
    Topic(
        "creator-os",
        "Creator OS",
        "CREATOR OPERATING SYSTEM",
        "창작의 속도는\n도구보다\n판단 기준에서 나옵니다.",
        ("무엇을 먼저\n결정하는가?", "어떤 작업을\n분리하는가?", "어디에서\n검토하는가?"),
        "창작의 속도는 도구를 더하는 데서만 나오지 않습니다. 먼저 결정할 것, 분리할 것, 검토할 것을 정리해보세요.",
        "창작팀의 병목은 대개 도구의 수가 아니라 판단 기준의 부재에서 생깁니다. 무엇을 먼저 결정하고, 어떤 작업을 분리하며, 어디에서 검토할지 정해야 합니다.\n\n출처: bbbb.beauty Creator OS 운영 프레임",
        "문제:\n도구를 늘려도 회의와 피드백이 줄지 않을 수 있습니다.\n\n해결:\n창작의 흐름을 결정, 분리, 검토의 세 단계로 정리합니다.\n\n실행:\n다음 제작 회의에서 결과물보다 판단 기준을 먼저 합의합니다.",
        "창작의 속도는 도구보다 판단 기준에서 나옵니다.",
    ),
    Topic(
        "media-art",
        "Media Art",
        "MEDIA ART",
        "보이는 장면은\n정보를 줄이는 것이 아니라\n이해를 시작하게 합니다.",
        ("무엇을 먼저\n보여줄까?", "어떤 흐름으로\n이해시킬까?", "무엇을 기억하게\n할까?"),
        "보이는 장면은 정보를 줄이는 것이 아니라 이해를 시작하게 합니다. 먼저 보여줄 것, 이해시킬 흐름, 남길 기억을 정리해보세요.",
        "복잡한 정보를 모두 화면에 넣는다고 이해가 늘어나지는 않습니다. 무엇을 먼저 보여주고, 어떤 흐름으로 이해시키며, 무엇을 기억하게 할지 정해야 합니다.\n\n출처: bbbb.beauty Media Art 운영 프레임",
        "문제:\n정보가 많을수록 고객은 핵심을 놓치기 쉽습니다.\n\n해결:\n장면을 이해의 순서로 설계합니다.\n\n실행:\n첫 장면은 하나의 질문만 제시하고, 다음 장면에서 근거와 의미를 연결합니다.",
        "좋은 장면은 정보를 줄이지 않고 이해의 순서를 만듭니다.",
    ),
    Topic(
        "ai-creative",
        "AI Creative",
        "AI CREATIVE",
        "AI의 가치는\n더 많은 초안이 아니라\n더 선명한 선택입니다.",
        ("무엇을 검증할\n가설인가?", "어떤 근거로\n선택할까?", "무엇을 다시\n학습할까?"),
        "AI의 가치는 더 많은 초안이 아니라 더 선명한 선택에 있습니다. 가설, 근거, 학습의 흐름으로 사용해보세요.",
        "AI는 초안을 빠르게 만들 수 있지만, 무엇을 선택할지는 대신 결정하지 않습니다. 가설을 세우고, 근거로 선택하며, 결과에서 다시 학습하는 구조가 필요합니다.\n\n출처: bbbb.beauty AI Creative 운영 프레임",
        "문제:\nAI 도입 뒤에도 피드백이 취향에 머물 수 있습니다.\n\n해결:\n가설, 근거, 학습의 순서로 AI 작업을 운영합니다.\n\n실행:\n프롬프트보다 먼저 이번 작업에서 검증할 가설을 문장으로 고정합니다.",
        "AI의 가치는 더 많은 초안이 아니라 더 선명한 선택입니다.",
    ),
    Topic(
        "brand-experience",
        "Brand Experience",
        "BRAND EXPERIENCE",
        "브랜드는\n보이는 말보다\n반복되는 경험으로 기억됩니다.",
        ("어디에서\n처음 만나는가?", "무엇을\n반복하는가?", "어떤 감각을\n남기는가?"),
        "브랜드는 보이는 말보다 반복되는 경험으로 기억됩니다. 첫 만남, 반복되는 장면, 남는 감각을 설계해보세요.",
        "브랜드 경험은 한 번의 캠페인으로 끝나지 않습니다. 고객이 처음 만나는 장면, 반복되는 행동, 남는 감각이 연결될 때 브랜드가 기억됩니다.\n\n출처: bbbb.beauty Brand Experience 운영 프레임",
        "문제:\n브랜드 메시지가 좋아도 경험이 반복되지 않으면 기억으로 남기 어렵습니다.\n\n해결:\n첫 만남, 반복, 감각의 세 요소를 하나의 흐름으로 설계합니다.\n\n실행:\n고객 여정에서 가장 자주 반복되는 장면 하나부터 점검합니다.",
        "브랜드는 문구보다 반복되는 경험으로 기억됩니다.",
    ),
    Topic(
        "creative-leadership",
        "Creative Leadership",
        "CREATIVE LEADERSHIP",
        "좋은 팀은\n정답보다\n리뷰 질문을 먼저 만듭니다.",
        ("무엇을 위한\n작업인가?", "무엇으로\n판단할까?", "어디까지\n지킬까?"),
        "좋은 팀은 정답보다 리뷰 질문을 먼저 만듭니다. 작업의 목적, 판단 기준, 지킬 선을 먼저 합의해보세요.",
        "좋은 창작 리더십은 답을 먼저 내놓는 일이 아닙니다. 작업의 목적, 판단 기준, 지킬 선을 팀이 함께 확인할 질문으로 만드는 일입니다.\n\n출처: bbbb.beauty Creative Leadership 운영 프레임",
        "문제:\n회의가 길어지는 이유는 의견이 많아서가 아니라 판단 기준이 없어서일 수 있습니다.\n\n해결:\n목적, 판단 기준, 가드레일을 리뷰 질문으로 고정합니다.\n\n실행:\n다음 리뷰에서 정답보다 질문을 먼저 공유합니다.",
        "좋은 팀은 정답보다 리뷰 질문을 먼저 만듭니다.",
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


def text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], value: str, size: int, fill: str, bold: bool = False, spacing: int = 10) -> None:
    draw.multiline_text(xy, value, font=font(size, bold), fill=fill, spacing=spacing)


def header(draw: ImageDraw.ImageDraw, topic: Topic, page: int) -> None:
    draw.rectangle((0, 0, 1080, 104), fill=BLACK)
    text(draw, (58, 34), f"bbbb / {topic.pillar.upper()}", 21, WHITE, True)
    text(draw, (930, 34), f"{page:02d} / 05", 21, CYAN, True)


def slide(topic: Topic, page: int, eyebrow: str, title: str, body: str) -> Image.Image:
    image = Image.new("RGB", (1080, 1080), IVORY)
    draw = ImageDraw.Draw(image)
    for position in range(0, 1081, 54):
        draw.line((position, 104, position, 1080), fill="#E0D9CD", width=1)
        draw.line((0, position, 1080, position), fill="#E0D9CD", width=1)
    header(draw, topic, page)
    draw.rectangle((58, 166, 312, 208), fill=BLACK)
    text(draw, (78, 176), eyebrow, 17, WHITE, True)
    text(draw, (58, 286), title, 58, BLACK, True, 8)
    text(draw, (58, 690), body, 29, MUTED, False, 8)
    text(draw, (58, 1018), "DAILY CONTENT SYSTEM", 17, MUTED, True)
    return image


def create_package(target_date: date, out_root: Path) -> Path:
    index = (target_date - ANCHOR_DATE).days % len(TOPICS)
    topic = TOPICS[index]
    out = out_root / f"{target_date.isoformat()}-{topic.slug}"
    carousel = out / "carousel"
    carousel.mkdir(parents=True, exist_ok=True)

    slides = [
        slide(topic, 1, topic.label, topic.headline, "브랜드 메시지는 장식보다 먼저\n고객의 선택을 설명해야 합니다."),
        slide(topic, 2, "QUESTION 01", topic.questions[0], "첫 장면은 정보가 아니라\n고객이 이해할 질문을 제시합니다."),
        slide(topic, 3, "QUESTION 02", topic.questions[1], "근거는 더 많이 나열하는 것이 아니라\n선택의 이유를 선명하게 만드는 일입니다."),
        slide(topic, 4, "QUESTION 03", topic.questions[2], "경험은 메시지를 끝내지 않습니다.\n다음 행동으로 이어질 때 의미가 생깁니다."),
        slide(topic, 5, "SAVE THIS", "멈춤 · 발견 · 행동\n세 단어로\n다음 리뷰를 시작하세요.", "bbbb.beauty는 브랜드를\n검증 가능한 경험 구조로 설계합니다."),
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
