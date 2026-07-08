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
FREE_PHOTO_ROOT = ROOT / "assets" / "free-image-backgrounds"
FONT_ROOT = ROOT / "assets" / "fonts"
DERMA_BIO_BACKGROUNDS = (
    PHOTO_ROOT / "derma-bio" / "02-lab-glassware.jpg",
    PHOTO_ROOT / "derma-bio" / "01-cosmetic-jar.jpg",
    PHOTO_ROOT / "kbeauty-ma" / "01-glass-building.jpg",
    PHOTO_ROOT / "kbeauty-ma" / "02-korean-cosmetics.jpg",
)

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
    "mechanism-in-motion": (
        *DERMA_BIO_BACKGROUNDS,
    ),
    "patient-understanding-system": (
        PHOTO_ROOT / "derma-bio" / "01-cosmetic-jar.jpg",
        PHOTO_ROOT / "derma-bio" / "02-lab-glassware.jpg",
        PHOTO_ROOT / "kbeauty-ma" / "02-korean-cosmetics.jpg",
        PHOTO_ROOT / "kbeauty-ma" / "01-glass-building.jpg",
    ),
    "pharma-visual-proof": (
        PHOTO_ROOT / "derma-bio" / "02-lab-glassware.jpg",
        PHOTO_ROOT / "kbeauty-ma" / "01-glass-building.jpg",
        PHOTO_ROOT / "derma-bio" / "01-cosmetic-jar.jpg",
        PHOTO_ROOT / "kbeauty-ma" / "02-korean-cosmetics.jpg",
    ),
    "medical-visual-production-standard": (
        *DERMA_BIO_BACKGROUNDS,
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


DG_MEDICAL_ANIMATION = Source(
    "DG Medical Animations Blog",
    "https://dgmedicalanimations.com/blog/",
    "2026",
    "Medical device and pharmaceutical products need 3D animation when conventional video cannot show the inside-body mechanism, MoA, or training sequence.",
)
AHA_MEDICAL_MARKETING = Source(
    "Aha Media Group - Medical Animation in Healthcare Marketing",
    "https://ahamediagroup.com/blog/medical-animations-for-hospitals-benefits/",
    "2024",
    "Medical animations explain procedures, medical-device use, drug action, anatomy, and post-care in short healthcare marketing and education videos.",
)
INTERVOKE_PATIENT_OUTCOMES = Source(
    "Intervoke - Medical Animation and Interactive 3D Anatomy",
    "https://www.intervoke.com/blog/how-medical-animation-and-interactive-3d-anatomy-improves-patient-outcomes",
    "2025",
    "MoA and MoD animations translate molecular, cellular, device, and treatment logic into visual explanations that support patient understanding and trust.",
)
GRAND_VIEW_MEDICAL_ANIMATION = Source(
    "Grand View Research - Medical Animation Market",
    "https://www.grandviewresearch.com/industry-analysis/medical-animation-market",
    "2025",
    "Medical animation demand is tied to pharmaceutical marketing, patient education, advanced research, drug MoA, and medical-device communication.",
)
MICROVERSE_SCIENCE_COMMUNICATION = Source(
    "Microverse Studios - Medical Animation Examples",
    "https://microversestudios.com/medical-animation-examples/",
    "2024",
    "Medical animation studios turn complex scientific stories into accurate visual narratives that are easier to grasp and remember.",
)


TOPICS = (
    Topic(
        "mechanism-in-motion",
        "Medical Animation Strategy",
        "MECHANISM IN MOTION",
        "좋은 메디컬 영상은\n제품을 보여주는 것이 아니라\n작동 원리를 보이게 합니다.",
        "메디컬 스킨케어와 의료기기 콘텐츠는 표면 이미지보다 보이지 않는 작용 기전을 이해 가능한 장면으로 바꾸는 일이 핵심입니다.",
        (
            ("체내 작동", "일반 촬영으로 보기 어려운 피부 흡수, 전달, 기기 작동은 3D 애니메이션이 설명력을 가집니다."),
            ("MoA", "약물·성분·기기 메시지는 Mechanism of Action을 시각화할 때 신뢰 구조가 선명해집니다."),
            ("교육", "환자와 HCP가 같은 장면을 보며 이해할 수 있어야 상담, 훈련, 마케팅 메시지가 분리되지 않습니다."),
        ),
        (
            ("보이는 것", "제품 컷만으로는 기술의 이유를 설명하기 어렵습니다."),
            ("이해되는 것", "작동 순서와 해부학적 맥락을 보여줄 때 메시지가 기억됩니다."),
        ),
        (
            "제품이 보여줘야 할 체내 장면을 먼저 정의합니다.",
            "MoA, MoD, device flow 중 어떤 설명 구조인지 구분합니다.",
            "Instagram은 장면, Facebook은 필요성, LinkedIn은 제작 기준으로 번역합니다.",
        ),
        (
            "보이지 않는 작동 원리",
            "소비자가 이해해야 할 순서",
            "의료진이 검토할 근거 범위",
            "영상으로만 설명 가능한 장면",
            "브랜드가 반복해야 할 과학 언어",
        ),
        "메디컬 영상의 후킹은 더 강한 효과 표현이 아니라 보이지 않는 작동 원리를 이해 가능한 장면으로 바꾸는 데서 시작됩니다.",
        "메디컬 스킨케어 콘텐츠에서 중요한 것은 제품을 예쁘게 보여주는 것만이 아닙니다.\n\n흡수, 전달, 보호, 재생, 기기 작동처럼 실제 선택 이유가 되는 부분은 눈에 보이지 않는 경우가 많습니다. 이때 3D 메디컬 애니메이션은 제품 컷이 설명하지 못하는 장면을 만들어 줍니다.\n\nBBBB가 먼저 확인하는 질문은 세 가지입니다.\n1. 이 제품은 어떤 체내 장면을 설명해야 하는가\n2. 소비자는 어떤 순서로 이해해야 하는가\n3. 의료진이나 브랜드 담당자는 어떤 근거 범위를 검토해야 하는가\n\n좋은 콘텐츠는 효과를 크게 말하기 전에 작동 원리를 분명하게 보여줍니다.",
        "문제:\n메디컬 스킨케어 브랜드는 성분과 기술을 말하지만, 고객은 실제로 무엇이 어떻게 작동하는지 보기 어렵습니다.\n\n해결:\n제품 컷, 임상 문구, 사용 장면을 먼저 만들기보다 보이지 않는 작동 원리를 장면 구조로 설계해야 합니다.\n\n실행:\nMoA, 피부 구조, 전달 경로, 사용 맥락을 분리하고 하나의 시각적 순서로 연결합니다.",
        "메디컬 영상은 제품보다 작동 원리를 먼저 보여줘야 합니다.",
        (DG_MEDICAL_ANIMATION, AHA_MEDICAL_MARKETING),
    ),
    Topic(
        "patient-understanding-system",
        "Patient Understanding System",
        "PATIENT CLARITY",
        "좋은 설명은\n정보를 더하는 것이 아니라\n환자가 따라갈 순서를 만듭니다.",
        "환자 교육용 메디컬 콘텐츠는 전문 용어를 줄이는 수준이 아니라 진단, 치료, 사용, 기대 결과를 하나의 이해 경로로 정리해야 합니다.",
        (
            ("이해", "환자는 의학 용어보다 자신의 상태와 선택지를 장면으로 이해할 때 질문을 만들 수 있습니다."),
            ("신뢰", "MoA와 치료 과정을 시각화하면 상담과 마케팅 메시지가 같은 기준으로 연결됩니다."),
            ("접근성", "짧은 애니메이션은 환자, 보호자, 의료진이 같은 설명을 반복해서 확인할 수 있게 합니다."),
        ),
        (
            ("전문성", "정확한 정보가 많아도 순서가 없으면 이해로 이어지지 않습니다."),
            ("친절함", "쉬운 표현만으로는 복잡한 치료나 기기 작동을 충분히 설명하기 어렵습니다."),
        ),
        (
            "환자가 먼저 알아야 할 질문을 정리합니다.",
            "진단, 치료, 사용법, 기대 결과를 단계별 장면으로 나눕니다.",
            "브랜드 메시지를 교육 자료와 분리하지 않고 같은 시각 언어로 설계합니다.",
        ),
        (
            "환자가 놓치는 첫 질문",
            "의료진 설명과 연결되는 장면",
            "반복 시청 가능한 짧은 구조",
            "과장 없이 말할 수 있는 기대 결과",
            "상담 이후에도 남는 기억 단서",
        ),
        "환자 교육 콘텐츠는 더 많은 설명보다 따라갈 수 있는 순서가 중요합니다. 애니메이션은 복잡한 정보를 기억 가능한 장면으로 바꿉니다.",
        "환자 교육에서 가장 큰 문제는 정보 부족이 아니라 이해 순서의 부재입니다.\n\n진단명, 성분명, 치료명, 사용법이 한 번에 제시되면 환자는 무엇을 먼저 이해해야 하는지 놓치기 쉽습니다. 메디컬 애니메이션은 이 정보를 장면의 순서로 바꿉니다.\n\nBBBB는 환자 교육형 콘텐츠를 만들 때 다음 구조를 봅니다.\n1. 환자가 먼저 궁금해할 질문\n2. 의료진 설명과 연결되는 핵심 장면\n3. 반복해서 볼 수 있는 짧은 흐름\n4. 과장 없이 말할 수 있는 기대 결과\n\n콘텐츠의 목표는 더 많이 말하는 것이 아니라 더 정확히 이해되게 만드는 것입니다.",
        "문제:\n복잡한 의학 정보는 정확하게 말해도 환자에게는 추상적으로 남을 수 있습니다.\n\n해결:\n전문 용어를 단순히 줄이는 것이 아니라 환자가 따라갈 수 있는 시각적 순서를 만들어야 합니다.\n\n실행:\n진단, 작용, 사용, 기대 결과를 한 번에 말하지 않고 장면 단위로 나누어 설계합니다.",
        "환자 교육 콘텐츠는 정보량보다 이해 순서가 먼저입니다.",
        (INTERVOKE_PATIENT_OUTCOMES, AHA_MEDICAL_MARKETING),
    ),
    Topic(
        "pharma-visual-proof",
        "Pharma Visual Proof",
        "SCIENCE TO STORY",
        "제약·바이오 메시지는\n데이터를 나열하는 순간보다\n작용을 보여줄 때 설득됩니다.",
        "제약·바이오 콘텐츠는 과학 데이터, MoA, 치료 경로, 시장 맥락을 시각적 내러티브로 바꿀 때 더 강한 커뮤니케이션 자산이 됩니다.",
        (
            ("시장", "의료 애니메이션 수요는 제약 마케팅, 환자 교육, 고도 연구 활용과 함께 성장하고 있습니다."),
            ("MoA", "Drug mechanism of action은 이론 설명만으로 이해하기 어려워 시각화 필요성이 높습니다."),
            ("세일즈", "질병 기전, 치료 과정, 약물 작용을 시각화하면 영업·교육 팀의 이해와 설명 효율이 높아집니다."),
        ),
        (
            ("데이터", "근거가 많아도 장면으로 번역되지 않으면 메시지는 어렵게 남습니다."),
            ("브랜드", "과학적 정확성과 기억되는 비주얼을 동시에 설계해야 합니다."),
        ),
        (
            "논문·임상·제품 자료에서 시각화할 핵심 작용을 고릅니다.",
            "세포, 조직, 기기, 환자 경로 중 주 설명 무대를 정합니다.",
            "과학 정확성, 브랜드 톤, 채널별 메시지를 동시에 검토합니다.",
        ),
        (
            "데이터가 말하는 핵심 작용",
            "시각화할 생물학적 무대",
            "브랜드가 가져갈 과학 언어",
            "HCP와 소비자 사이의 설명 차이",
            "투자자와 파트너에게 남길 기억 장면",
        ),
        "제약·바이오 메시지는 데이터 자체보다 데이터가 어떤 작용을 설명하는지 보여줄 때 강해집니다.",
        "제약·바이오 콘텐츠에서 데이터는 출발점이지 완성된 메시지가 아닙니다.\n\nDrug MoA, 치료 경로, 세포 수준의 변화, 의료기기 작동은 텍스트만으로 전달하면 이해 장벽이 높습니다. 그래서 메디컬 애니메이션은 과학 자료를 단순히 예쁘게 만드는 작업이 아니라, 어떤 작용을 어떤 순서로 보여줄지 결정하는 전략 작업입니다.\n\nBBBB 적용 기준은 다음과 같습니다.\n1. 데이터가 말하는 핵심 작용을 고릅니다.\n2. 세포, 조직, 기기, 환자 경로 중 설명 무대를 정합니다.\n3. 과학 정확성과 브랜드 기억 장면을 동시에 설계합니다.\n4. HCP, 투자자, 소비자에게 남길 메시지를 분리합니다.\n\n좋은 영상은 정보를 줄이지 않습니다. 이해 가능한 구조로 바꿉니다.",
        "문제:\n제약·바이오 브랜드는 근거가 많지만, 그 근거가 어떤 작용을 설명하는지 한눈에 보이지 않는 경우가 많습니다.\n\n해결:\n데이터를 카피로 요약하기 전에 MoA, 치료 경로, 생물학적 무대를 시각 내러티브로 바꿔야 합니다.\n\n실행:\n과학 정확성, 브랜드 기억 장면, 채널별 설명 깊이를 동시에 설계합니다.",
        "제약·바이오 영상은 데이터를 줄이는 것이 아니라 작용을 보이게 하는 일입니다.",
        (GRAND_VIEW_MEDICAL_ANIMATION, MICROVERSE_SCIENCE_COMMUNICATION),
    ),
    Topic(
        "medical-visual-production-standard",
        "Medical Visual Production Standard",
        "PRODUCTION STANDARD",
        "전문적인 메디컬 콘텐츠는\n멋진 이미지보다\n검증 가능한 제작 기준에서 나옵니다.",
        "메디컬 애니메이션 제작사는 미감, 과학 정확성, 규제 가능한 표현, 채널별 사용 목적을 하나의 제작 기준으로 정리해야 합니다.",
        (
            ("정확성", "복잡한 과학 이야기는 아름다운 이미지보다 먼저 정확한 구조와 전문가 검토가 필요합니다."),
            ("기억성", "좋은 메디컬 애니메이션은 과학을 이해하기 쉽고 기억에 남는 시각 이야기로 바꿉니다."),
            ("목적", "환자 교육, 제품 마케팅, HCP 훈련, 투자자 설명은 같은 영상 언어를 쓰더라도 설계 기준이 다릅니다."),
        ),
        (
            ("미감", "보기 좋은 비주얼만으로는 의료 콘텐츠의 신뢰를 만들 수 없습니다."),
            ("검증", "검토 구조가 없으면 과학 메시지와 브랜드 표현이 쉽게 어긋납니다."),
        ),
        (
            "영상 목적을 환자 교육, HCP, 마케팅, 투자자 설명으로 구분합니다.",
            "시각 은유를 쓰기 전에 과학적으로 고정해야 할 사실을 정합니다.",
            "검수 가능한 스토리보드와 표현 범위를 먼저 만듭니다.",
        ),
        (
            "목적별 시청자",
            "과학적으로 고정해야 할 사실",
            "쓸 수 있는 시각 은유",
            "규제와 브랜드 표현의 경계",
            "검수 가능한 스토리보드",
        ),
        "메디컬 애니메이션의 전문성은 이미지 퀄리티만이 아니라 과학적으로 검수 가능한 제작 기준에서 나옵니다.",
        "전문적인 메디컬 콘텐츠는 멋진 이미지에서 시작하지 않습니다.\n\n먼저 목적을 나눠야 합니다. 환자 교육인지, 의료기기 사용 설명인지, HCP 훈련인지, 제약·바이오 투자자 커뮤니케이션인지에 따라 필요한 장면과 표현 범위가 달라집니다.\n\nBBBB는 제작 전 다음 기준을 확인합니다.\n1. 시청자가 누구인가\n2. 과학적으로 고정해야 할 사실은 무엇인가\n3. 어떤 시각 은유를 사용할 수 있는가\n4. 규제와 브랜드 표현의 경계는 어디인가\n5. 검수 가능한 스토리보드가 있는가\n\n메디컬 애니메이션은 예쁜 영상이 아니라 검증 가능한 설명 구조입니다.",
        "문제:\n메디컬 콘텐츠는 시각적으로 좋아 보여도 과학적 검수 구조가 없으면 신뢰를 만들기 어렵습니다.\n\n해결:\n제작 전 목적, 시청자, 고정 사실, 표현 범위, 검수 기준을 먼저 정의해야 합니다.\n\n실행:\n스토리보드 단계에서 과학 정확성, 시각 은유, 채널별 사용 목적을 함께 검토합니다.",
        "메디컬 애니메이션의 품질은 렌더보다 검수 가능한 제작 기준에서 갈립니다.",
        (MICROVERSE_SCIENCE_COMMUNICATION, DG_MEDICAL_ANIMATION),
    ),
)


def font_path(bold: bool) -> Path:
    candidates = [
        os.getenv("FONT_BOLD" if bold else "FONT_REGULAR", ""),
        FONT_ROOT / ("Paperlogy-7Bold.ttf" if bold else "Paperlogy-4Regular.ttf"),
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
    synced = sorted((FREE_PHOTO_ROOT / topic.slug).glob("*.jpg")) + sorted((FREE_PHOTO_ROOT / topic.slug).glob("*.png"))
    fallback = list(PHOTO_BACKGROUNDS.get(topic.slug, ()))
    candidates = []
    seen = set()
    for path in [*synced, *fallback]:
        if not path.is_file():
            continue
        key = path.resolve()
        if key in seen:
            continue
        seen.add(key)
        candidates.append(path)
    if not candidates:
        raise FileNotFoundError(f"No photo backgrounds configured for topic slug: {topic.slug}")

    variant = PAGE_VARIANTS[(page - 1) % len(PAGE_VARIANTS)]
    source_index = (page - 1) % len(candidates)
    source = candidates[source_index]
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
    if page > len(candidates) and len(candidates) > 1:
        secondary_index = (source_index + max(1, len(candidates) // 2)) % len(candidates)
        secondary = Image.open(candidates[secondary_index])
        secondary = ImageOps.exif_transpose(secondary).convert("RGB")
        secondary = ImageOps.fit(
            secondary,
            (round(WIDTH / float(variant["zoom"])), round(HEIGHT / float(variant["zoom"]))),
            method=Image.Resampling.LANCZOS,
            centering=(1 - float(variant["center"][0]), float(variant["center"][1])),
        )
        secondary = secondary.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        secondary = ImageOps.mirror(secondary)
        secondary = ImageEnhance.Color(secondary).enhance(0.58)
        secondary = ImageEnhance.Contrast(secondary).enhance(1.08)
        photo = Image.blend(photo, secondary, 0.42)
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
    draw_text(draw, (SAFE_X + 3, 75), f"bbbb / {topic.pillar.upper()}", 17, (0, 0, 0, 150), True)
    draw_text(draw, (SAFE_X, 72), f"bbbb / {topic.pillar.upper()}", 17, WHITE, True)
    draw_text(draw, (SAFE_RIGHT - 25, 75), f"{page:02d}/05", 17, (0, 0, 0, 150), True, anchor="ra")
    draw_text(draw, (SAFE_RIGHT - 28, 72), f"{page:02d}/05", 17, AQUA, True, anchor="ra")
    draw_text(draw, (SAFE_X + 3, 157), section, 15, (0, 0, 0, 150), True)
    draw_text(draw, (SAFE_X, 154), section, 15, WHITE, True)


def footer(draw: ImageDraw.ImageDraw) -> None:
    draw_text(draw, (SAFE_X, 1012), "BBBB BEAUTY INTELLIGENCE", 14, (255, 255, 255, 220), True)
    draw_text(draw, (SAFE_RIGHT, 1012), "SAVE / SHARE", 13, (255, 255, 255, 220), True, anchor="ra")


def title(draw: ImageDraw.ImageDraw, y: int, value: str, size: int = 54, color: str = WHITE) -> None:
    size = fit_text(draw, value, SAFE_RIGHT - SAFE_X, size, 36)
    draw_text(draw, (SAFE_X + 3, y + 3), value, size, (0, 0, 0, 145), True, 10)
    draw_text(draw, (SAFE_X, y), value, size, color, True, 10)


def translucent_panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], alpha: int = 205) -> None:
    return None


LINKEDIN_ENGLISH_BRIEFS = {
    "kbeauty-ma-system-risk": {
        "problem": "K-beauty M&A stories often focus on acquisition size, but the operational risk appears after the deal: channel control, product cadence, decision speed, and brand memory.",
        "frame": "For medical skincare and beauty brands, content should explain what changes when a fast local brand enters a global operating system.",
        "questions": (
            "Which part of the brand system becomes slower after acquisition?",
            "Which product or claim still needs local speed to stay credible?",
            "Which scene can show the gap between headquarters logic and market behavior?",
        ),
    },
    "derma-cosmetic-expansion": {
        "problem": "Dermocosmetic brands are expanding across skincare, functional cosmetics, beauty devices, and bio-adjacent claims, but audiences do not trust expansion just because the category sounds scientific.",
        "frame": "The content task is to show what has been validated, what is still a brand promise, and where the consumer should place attention.",
        "questions": (
            "Which ingredient, device, or claim is actually central?",
            "What use case makes the benefit understandable?",
            "What evidence boundary should the brand respect?",
        ),
    },
    "clinical-proof-translation": {
        "problem": "Clinical or scientific proof can lose value when it is presented as a dense list of terms instead of a decision pathway.",
        "frame": "A stronger post translates evidence into sequence: what the product does, when it matters, and what the viewer can reasonably infer.",
        "questions": (
            "What is the minimum proof the audience must understand first?",
            "Which claim needs a visual explanation rather than a slogan?",
            "How should the channel separate education from promotion?",
        ),
    },
    "post-acquisition-brand-system": {
        "problem": "After acquisition, a beauty brand can keep its name but lose the operating rhythm that made the brand distinctive.",
        "frame": "Content should make the invisible system visible: decision layers, portfolio logic, launch rhythm, and consumer trust signals.",
        "questions": (
            "Which brand behavior changed after acquisition?",
            "What consumer signal shows whether trust is holding?",
            "Which visual scene can explain the system shift without overclaiming?",
        ),
    },
    "mechanism-in-motion": {
        "problem": "Medical skincare content often says absorption, delivery, protection, or regeneration without showing how the mechanism works.",
        "frame": "3D medical animation should turn an invisible mechanism into a sequence viewers can inspect, remember, and discuss.",
        "questions": (
            "Which mechanism is invisible in ordinary product photography?",
            "Which step should be shown first for patient or consumer understanding?",
            "Which claim must remain within a medically reviewable boundary?",
        ),
    },
    "patient-understanding-system": {
        "problem": "A patient or consumer rarely rejects content because it is not beautiful enough. They disengage when the explanation is not ordered.",
        "frame": "The useful system is a clarity ladder: context, mechanism, evidence, practical relevance, and next question.",
        "questions": (
            "What does the viewer need to understand before the product benefit?",
            "Which visual scene reduces confusion fastest?",
            "Where should clinical, marketing, and sales language be separated?",
        ),
    },
    "pharma-visual-proof": {
        "problem": "Pharma and bio messages often contain evidence, but evidence alone does not explain how a mechanism works or why a choice matters.",
        "frame": "A visual proof system should connect mechanism of action, treatment context, evidence limits, and channel-specific messaging.",
        "questions": (
            "Which mechanism needs to be visualized before the claim is persuasive?",
            "Which evidence boundary should be made explicit?",
            "How should the same science be translated for Instagram, Facebook, and LinkedIn?",
        ),
    },
    "medical-visual-production-standard": {
        "problem": "Medical visual content fails when it looks polished but cannot support review, education, or commercial reuse.",
        "frame": "A production standard should connect scientific accuracy, visual hierarchy, review workflow, and the business use of each asset.",
        "questions": (
            "Which part of the content needs medical review first?",
            "Which visual decision affects comprehension most?",
            "How can one asset serve education, sales, and brand trust without becoming vague?",
        ),
    },
}


def linkedin_english_post_for(topic: Topic, source_lines: str) -> str:
    brief = LINKEDIN_ENGLISH_BRIEFS[topic.slug]
    questions = "\n".join(f"{index}. {item}" for index, item in enumerate(brief["questions"], start=1))
    return (
        f"{topic.pillar} / bbbb.beauty\n\n"
        f"Problem:\n{brief['problem']}\n\n"
        f"Operating frame:\n{brief['frame']}\n\n"
        "Questions to solve before production:\n"
        f"{questions}\n\n"
        "BBBB production view:\n"
        "A strong medical skincare post is not a decorated claim. It is a structured explanation system: mechanism, evidence, context, and channel role should move together.\n\n"
        "Channel translation:\n"
        "- Instagram: make the mechanism visually immediate.\n"
        "- Facebook: explain why the claim matters.\n"
        "- LinkedIn: show how the production logic can be reviewed and reused.\n\n"
        "Reference links:\n"
        f"{source_lines}"
    )


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
        draw_text(draw, (SAFE_X + 3, y + 3), name, 25, (0, 0, 0, 150), True)
        draw_text(draw, (SAFE_X, y), name, 25, AQUA, True)
        draw_text(draw, (SAFE_X + 3, y + 41), wrap(fact, 34), 24, (0, 0, 0, 150), False, 7)
        draw_text(draw, (SAFE_X, y + 38), wrap(fact, 34), 24, WHITE, False, 7)
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
        draw_text(draw, (SAFE_X + 3, y + 3), f"{idx}. {label}", 31, (0, 0, 0, 150), True)
        draw_text(draw, (SAFE_X, y), f"{idx}. {label}", 31, AQUA, True)
        draw_text(draw, (SAFE_X + 3, y + 66), wrap(detail, 29), 28, (0, 0, 0, 150), False, 10)
        draw_text(draw, (SAFE_X, y + 63), wrap(detail, 29), 28, (255, 255, 255, 238), False, 10)
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
        draw_text(draw, (SAFE_X + 3, y + 3), f"{idx:02d}", 25, (0, 0, 0, 150), True)
        draw_text(draw, (SAFE_X, y), f"{idx:02d}", 25, AQUA, True)
        draw_text(draw, (SAFE_X + 84 + 3, y + 3), wrap(item, 29), 27, (0, 0, 0, 150), True, 6)
        draw_text(draw, (SAFE_X + 84, y), wrap(item, 29), 27, WHITE, True, 6)
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
        draw_text(draw, (SAFE_X + 3, y + 3), f"{idx:02d}", 25, (0, 0, 0, 150), True)
        draw_text(draw, (SAFE_X, y), f"{idx:02d}", 25, AQUA, True)
        draw_text(draw, (SAFE_X + 84 + 3, y + 3), wrap(item, 28), 28, (0, 0, 0, 150), True, 5)
        draw_text(draw, (SAFE_X + 84, y), wrap(item, 28), 28, WHITE, True, 5)
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


def facebook_post_for(topic: Topic) -> str:
    evidence_lines = "\n".join(f"- {name}: {fact}" for name, fact in topic.evidence)
    checklist_lines = "\n".join(f"{index}. {item}" for index, item in enumerate(topic.checklist[:4], start=1))
    return (
        f"{topic.facebook}\n\n"
        "전문가 관점:\n"
        "메디컬 애니메이션 콘텐츠의 문제는 시각 자료가 부족한 것이 아니라 설명의 위계가 정리되지 않은 경우가 많다는 점입니다. "
        "과학 근거, 작용 기전, 사용 장면, 규제 가능한 표현을 같은 높이로 말하면 시청자는 무엇을 먼저 이해해야 하는지 판단하기 어렵습니다.\n\n"
        "이번 콘텐츠에서 읽어야 할 제작 신호:\n"
        f"{evidence_lines}\n\n"
        "BBBB 적용 프레임:\n"
        f"{checklist_lines}\n\n"
        "결론:\n"
        "좋은 메디컬 콘텐츠는 제품을 더 크게 포장하는 것이 아니라, 시청자가 과학적 선택을 검토할 수 있는 기준을 남깁니다. "
        "그래서 이미지, 카피, 근거, 채널 역할이 하나의 설명 구조로 연결되어야 합니다."
    )


def linkedin_post_for(topic: Topic, source_lines: str) -> str:
    production_lines = "\n".join(f"{index}. {item}" for index, item in enumerate(topic.production, start=1))
    checklist_lines = "\n".join(f"- {item}" for item in topic.checklist)
    return (
        f"{topic.linkedin}\n\n"
        "왜 중요한가:\n"
        "메디컬 스킨케어와 의료기기 시장에서 콘텐츠는 더 이상 단순한 홍보물이 아닙니다. "
        "과학 근거와 작용 기전을 말하는 동시에 규제 가능한 표현, 환자·소비자 이해도, HCP 검토 맥락을 함께 관리해야 하는 제작 자산입니다.\n\n"
        "실행 기준:\n"
        f"{production_lines}\n\n"
        "검토 체크리스트:\n"
        f"{checklist_lines}\n\n"
        "실무적으로는 한 개의 게시물을 만들기 전에 먼저 세 가지 질문을 확인합니다. "
        "첫째, 어떤 보이지 않는 작용을 보여줘야 하는가. 둘째, 어떤 근거와 표현 범위 안에서 말할 수 있는가. "
        "셋째, Instagram, Facebook, LinkedIn에서 각각 어떤 깊이로 번역되는가.\n\n"
        "참고 자료:\n"
        f"{source_lines}"
    )


def validate_topic_assets(topic: Topic) -> None:
    configured = PHOTO_BACKGROUNDS.get(topic.slug)
    if not configured:
        raise FileNotFoundError(f"No photo backgrounds configured for topic slug: {topic.slug}")
    missing = [str(path) for path in configured if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            f"Missing photo background assets for topic slug {topic.slug}: " + ", ".join(missing)
        )


def create_package(target_date: date, out_root: Path) -> Path:
    index = (target_date - ANCHOR_DATE).days % len(TOPICS)
    topic = TOPICS[index]
    validate_topic_assets(topic)
    out = out_root / f"{target_date.isoformat()}-{topic.slug}"
    carousel = out / "carousel"
    instagram_carousel = out / "instagram-carousel"
    carousel.mkdir(parents=True, exist_ok=True)
    instagram_carousel.mkdir(parents=True, exist_ok=True)

    slides = [
        slide_hook(topic),
        slide_evidence(topic),
        slide_dilemma(topic),
        slide_production(topic),
        slide_checklist(topic),
    ]
    for page, image in enumerate(slides, start=1):
        image.save(carousel / f"{page:02d}.png", quality=95)
        image.convert("RGB").save(instagram_carousel / f"{page:02d}.jpg", quality=92, optimize=True)

    source_lines = "\n".join(f"- {source.title} ({source.date}) {source.url}" for source in topic.sources)
    (out / "instagram-caption.txt").write_text(instagram_caption_for(topic, target_date), encoding="utf-8")
    (out / "facebook-caption.txt").write_text(facebook_post_for(topic), encoding="utf-8")
    (out / "linkedin-post.txt").write_text(linkedin_post_for(topic, source_lines), encoding="utf-8")
    (out / "linkedin-post-en.txt").write_text(linkedin_english_post_for(topic, source_lines), encoding="utf-8")
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
        f"- Source: Medical animation and healthcare communication source study\n"
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
