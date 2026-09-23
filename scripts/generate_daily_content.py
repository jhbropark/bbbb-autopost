#!/usr/bin/env python3
"""Generate a date-specific bbbb.beauty social package for the daily workflow."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
import hashlib
import json
import os
from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
ANCHOR_DATE = date(2026, 6, 22)
CONTENT_POLICY_PATH = ROOT / "config" / "content_policy.json"

NAVY = "#1E293B"
WHITE = "#FFFFFF"
AQUA = "#0EA5E9"
SOFT = "#F8F6F2"
INK = "#111827"

WIDTH = 1080
HEIGHT = 1080
SAFE_X = 104
SAFE_RIGHT = 976
EDGE = 4
FREE_PHOTO_ROOT = ROOT / "assets" / "free-image-backgrounds"
FONT_ROOT = ROOT / "assets" / "fonts"
MIN_UNIQUE_TOPIC_IMAGES = 5
BRAND_WORDMARK = "BBBB BEAUTY"
BRAND_SERIES = "BEAUTY INTELLIGENCE"
CTA_BY_PAGE = {
    1: "밀어서 보기 ->",
    2: "다음: 작동 장면 ->",
    3: "다음: 검토 기준 ->",
    4: "마지막은 저장 기준 ->",
    5: "저장해두면 다시 볼 수 있어요",
}
INSTAGRAM_HASHTAGS = (
    "#BBBBBeauty",
    "#MedicalAesthetics",
    "#BeautyMarketing",
    "#MedicalContent",
    "#BrandExperience",
    "#ContentStrategy",
)
INSTAGRAM_HOOKS = {
    "mechanism-in-motion": (
        "\uc81c\ud488 \uc0ac\uc9c4\ub9cc\uc73c\ub85c\ub294 \uc65c \uc791\ub3d9\ud558\ub294\uc9c0 \uc124\uba85\ub418\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4.\n"
        "\uccab \uc7a5\uc5d0\uc11c \ubcf4\uc774\uc9c0 \uc54a\ub294 \uc6d0\ub9ac\ub97c \uba3c\uc800 \uc7a1\uc544\uc57c \uc800\uc7a5\ub429\ub2c8\ub2e4."
    ),
    "patient-understanding-system": (
        "\ud658\uc790\ub294 \uc815\ubcf4\ub7c9\ubcf4\ub2e4 \ub2e4\uc74c\uc5d0 \ubb34\uc5c7\uc744 \ubd10\uc57c \ud558\ub294\uc9c0\uc5d0 \ubc18\uc751\ud569\ub2c8\ub2e4.\n"
        "\uc88b\uc740 \uad50\uc721 \ucf58\ud150\uce20\ub294 \uc9c8\ubb38\uc758 \uc21c\uc11c\ub97c \uba3c\uc800 \uc124\uacc4\ud569\ub2c8\ub2e4."
    ),
    "pharma-visual-proof": (
        "\uadfc\uac70\uac00 \ub9ce\uc744\uc218\ub85d \ub354 \uc27d\uac8c \ubcf4\uc5ec\uc57c \ud569\ub2c8\ub2e4.\n"
        "\ub370\uc774\ud130\ub97c \uc7a5\uba74\uc73c\ub85c \ubc88\uc5ed\ud560 \ub54c \uc2e0\ub8b0\uac00 \uc0dd\uae41\ub2c8\ub2e4."
    ),
    "medical-visual-production-standard": (
        "\uba4b\uc9c4 \uc758\ub8cc \uc774\ubbf8\uc9c0\ub294 \ucda9\ubd84\ud558\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4.\n"
        "\uac80\ud1a0 \uac00\ub2a5\ud55c \uc81c\uc791 \uae30\uc900\uc774 \uc788\uc5b4\uc57c \ube0c\ub79c\ub4dc \uc790\uc0b0\uc774 \ub429\ub2c8\ub2e4."
    ),
}
INSTAGRAM_CAPTION_HOOKS = {
    "mechanism-in-motion": "\uc65c \uc88b\uc740 \uba54\ub514\uceec \uc601\uc0c1\uc740 \uc81c\ud488\ubcf4\ub2e4 \uc791\ub3d9 \uc7a5\uba74\uc744 \uba3c\uc800 \ubcf4\uc5ec\uc904\uae4c\uc694?",
    "patient-understanding-system": "\ud658\uc790 \uad50\uc721 \ucf58\ud150\uce20\uc5d0\uc11c \uac00\uc7a5 \uba3c\uc800 \ubcf4\uc5ec\uc918\uc57c \ud560 \uc7a5\uba74\uc740 \ubb34\uc5c7\uc77c\uae4c\uc694?",
    "pharma-visual-proof": "\uc784\uc0c1 \uadfc\uac70\uac00 \ub9ce\uc744\uc218\ub85d \uc65c \ub354 \ub2e8\uc21c\ud55c \uc7a5\uba74 \uc124\uacc4\uac00 \ud544\uc694\ud560\uae4c\uc694?",
    "medical-visual-production-standard": "\uc758\ub8cc \ucf58\ud150\uce20\uac00 \uba4b\uc9c4 \uc774\ubbf8\uc9c0\uc5d0\uc11c \ub05d\ub098\uc9c0 \uc54a\uc73c\ub824\uba74 \ubb34\uc5c7\uc744 \uba3c\uc800 \uc815\ud574\uc57c \ud560\uae4c\uc694?",
}
INSTAGRAM_SAVE_POINT = "\uc800\uc7a5 \ud3ec\uc778\ud2b8: \uc791\ub3d9 \uc6d0\ub9ac / \uc774\ud574 \uc21c\uc11c / \uac80\ud1a0 \uae30\uc900"
INSTAGRAM_DEFAULT_HOOK = "\uc624\ub298 \ucf58\ud150\uce20\uc5d0\uc11c \uba3c\uc800 \ubd10\uc57c \ud560 \uc7a5\uba74\uc740 \ubb34\uc5c7\uc77c\uae4c\uc694?"
INSTAGRAM_OBSERVATION_LABEL = "\uc624\ub298\uc758 \uad00\ucc30"
INSTAGRAM_SAVE_CRITERION = "\uc800\uc7a5\ud574\ub458 \uae30\uc900: \uc815\ubcf4\ubcf4\ub2e4 \uba3c\uc800 \ubcf4\uc774\ub294 \uc7a5\uba74\uc774 \uc120\ud0dd \uc774\uc720\ub97c \ub9cc\ub4ed\ub2c8\ub2e4."
PAGE_VARIANTS = (
    {"photo": 0, "center": (0.38, 0.45), "zoom": 1.00, "blur": 0.15, "mirror": False, "tint": (5, 14, 24)},
    {"photo": 1, "center": (0.55, 0.52), "zoom": 1.08, "blur": 0.10, "mirror": False, "tint": (10, 20, 28)},
    {"photo": 0, "center": (0.68, 0.42), "zoom": 1.22, "blur": 0.18, "mirror": True, "tint": (9, 22, 32)},
    {"photo": 1, "center": (0.32, 0.60), "zoom": 1.18, "blur": 0.12, "mirror": True, "tint": (15, 22, 32)},
    {"photo": 0, "center": (0.50, 0.64), "zoom": 1.35, "blur": 0.18, "mirror": False, "tint": (6, 20, 31)},
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


def load_topic_photo(topic: Topic, page: int) -> Image.Image:
    source = topic_photo_source(topic, page)
    variant = PAGE_VARIANTS[(page - 1) % len(PAGE_VARIANTS)]
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
    photo = ImageEnhance.Color(photo).enhance(0.72)
    photo = ImageEnhance.Contrast(photo).enhance(1.22)
    blur = max(0.0, float(variant["blur"]) - 0.6)
    return photo.convert("RGBA").filter(ImageFilter.GaussianBlur(blur))


def topic_photo_candidates(topic: Topic) -> list[Path]:
    synced_jpg = sorted((FREE_PHOTO_ROOT / topic.slug).glob("*.jpg")) + sorted(
        (FREE_PHOTO_ROOT / topic.slug).glob("*.jpeg")
    )
    synced_png = sorted((FREE_PHOTO_ROOT / topic.slug).glob("*.png"))
    candidates = []
    seen = set()
    for path in [*synced_jpg, *synced_png]:
        if not path.is_file():
            continue
        key = path.resolve()
        if key in seen:
            continue
        seen.add(key)
        candidates.append(path)
    return candidates


def topic_photo_source(topic: Topic, page: int) -> Path:
    candidates = topic_photo_candidates(topic)
    if len(candidates) < MIN_UNIQUE_TOPIC_IMAGES:
        raise FileNotFoundError(
            f"Need at least {MIN_UNIQUE_TOPIC_IMAGES} unique image assets for topic slug "
            f"{topic.slug}; found {len(candidates)}. Run scripts/sync_topic_image_assets.py. "
            "Generic fallback backgrounds are not allowed for publishing."
        )
    source_index = (page - 1) % len(candidates)
    return candidates[source_index]


def topic_asset_credits(topic: Topic) -> dict[str, dict[str, str]]:
    credits_path = FREE_PHOTO_ROOT / topic.slug / "credits.json"
    if not credits_path.exists():
        return {}
    try:
        payload = json.loads(credits_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    credits: dict[str, dict[str, str]] = {}
    for item in payload:
        if isinstance(item, dict) and item.get("file"):
            credits[str(item["file"])] = {
                "provider": str(item.get("provider", "")),
                "source_url": str(item.get("source_url", "")),
                "query": str(item.get("query", "")),
            }
    return credits


def add_photo_background(image: Image.Image, topic: Topic, page: int) -> None:
    photo = load_topic_photo(topic, page)
    variant = PAGE_VARIANTS[(page - 1) % len(PAGE_VARIANTS)]
    tint = Image.new("RGBA", image.size, (*variant["tint"], 34))
    photo = Image.alpha_composite(photo, tint)

    shade = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shade_draw = ImageDraw.Draw(shade)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        alpha = int(8 + 74 * (ratio ** 1.1))
        shade_draw.line((0, y, WIDTH, y), fill=(30, 41, 59, alpha))
    for x in range(WIDTH):
        alpha = int(54 * (1 - min(1, x / 760)))
        shade_draw.line((x, 0, x, HEIGHT), fill=(10, 16, 27, alpha))

    image.alpha_composite(photo)
    image.alpha_composite(shade)


def header(draw: ImageDraw.ImageDraw, topic: Topic, page: int, section: str) -> None:
    draw_text(draw, (SAFE_X + 3, 73), BRAND_WORDMARK, 23, (0, 0, 0, 150), True, 2)
    draw_text(draw, (SAFE_X, 70), BRAND_WORDMARK, 23, WHITE, True, 2)
    draw_text(draw, (SAFE_RIGHT + 3, 73), f"{page}/05", 23, (0, 0, 0, 150), True, anchor="ra")
    draw_text(draw, (SAFE_RIGHT, 70), f"{page}/05", 23, SOFT, True, anchor="ra")
    if page > 1:
        draw_text(draw, (SAFE_X + 4, 183), f"{page - 1:02d}", 94, (0, 0, 0, 110), True)
        draw_text(draw, (SAFE_X, 178), f"{page - 1:02d}", 94, (232, 226, 214, 238), True)


def footer(draw: ImageDraw.ImageDraw) -> None:
    draw_text(draw, (SAFE_X, 1016), BRAND_SERIES, 14, (255, 255, 255, 214), True)
    draw_text(draw, (SAFE_RIGHT, 1016), "SAVE / SHARE", 13, (255, 255, 255, 214), True, anchor="ra")


def title(draw: ImageDraw.ImageDraw, y: int, value: str, size: int = 54, color: str = WHITE) -> None:
    size = fit_text(draw, value, SAFE_RIGHT - SAFE_X, size, 36)
    draw_text(draw, (SAFE_X + 3, y + 3), value, size, (0, 0, 0, 145), True, 10)
    draw_text(draw, (SAFE_X, y), value, size, color, True, 10)


def case_slide_copy(topic: Topic, page: int) -> tuple[str, str, str]:
    return CASE_STUDY_SLIDES[topic.slug][page - 1]


def draw_feed_gradient(image: Image.Image) -> None:
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        bottom = max(0, (ratio - 0.50) / 0.50)
        top = max(0, (0.18 - ratio) / 0.18)
        alpha = int(10 + 220 * (bottom ** 1.55) + 36 * top)
        draw.line((0, y, WIDTH, y), fill=(0, 0, 0, min(244, alpha)))
    image.alpha_composite(overlay)


def draw_feed_label(draw: ImageDraw.ImageDraw, label: str, page: int) -> None:
    label_text = label.upper()
    if page == 1:
        y = 660
    elif page == 5:
        y = 604
    else:
        y = 636
    draw_text(draw, (SAFE_X + 2, y + 2), label_text, 18, (0, 0, 0, 150), True, 2)
    draw_text(draw, (SAFE_X, y), label_text, 18, (248, 246, 242, 230), True, 2)


def draw_progress_bar(draw: ImageDraw.ImageDraw, page: int) -> None:
    bar_y = HEIGHT - 8
    draw.rectangle((0, bar_y, WIDTH, HEIGHT), fill=(8, 8, 8, 255))
    draw.rectangle((0, bar_y, round(WIDTH * page / 5), HEIGHT), fill=(232, 226, 214, 255))


def draw_cta(draw: ImageDraw.ImageDraw, page: int) -> None:
    cta = CTA_BY_PAGE.get(page, "밀어서 보기 ->")
    draw_text(draw, (SAFE_X + 2, 968), cta, 22, (0, 0, 0, 155), True, 2)
    draw_text(draw, (SAFE_X, 966), cta, 22, SOFT, True, 2)


def draw_save_callout(draw: ImageDraw.ImageDraw) -> None:
    box = (SAFE_X, 814, SAFE_RIGHT, 942)
    draw.rounded_rectangle(box, radius=18, outline=(255, 255, 255, 62), width=2, fill=(0, 0, 0, 54))
    draw_text(draw, (SAFE_X + 36, 846), "저장 포인트", 23, (232, 226, 214, 238), True, 2)
    draw_text(
        draw,
        (SAFE_X + 36, 886),
        "작동 원리 / 이해 순서 / 검토 기준",
        29,
        WHITE,
        True,
        3,
    )


def draw_feed_headline(draw: ImageDraw.ImageDraw, headline: str, subline: str, page: int) -> None:
    if page == 1:
        y = 706
        start_size = 72
    elif page == 5:
        y = 652
        start_size = 58
    else:
        y = 704
        start_size = 64
    headline_text = wrap(headline, 19 if page == 1 else 20)
    size = fit_text(draw, headline_text, SAFE_RIGHT - SAFE_X, start_size, 42)
    while text_height(headline_text, size, True, 10) > 236 and size > 42:
        size -= 2
    draw_text(draw, (SAFE_X + 3, y + 3), headline_text, size, (0, 0, 0, 165), True, 10)
    draw_text(draw, (SAFE_X, y), headline_text, size, WHITE, True, 10)

    subline_text = wrap(subline, 28)
    subline_y = y + text_height(headline_text, size, True, 10) + 32
    if page == 5:
        max_subline_y = 792
    else:
        max_subline_y = 926
    if subline_y + text_height(subline_text, 29, False, 10) < max_subline_y:
        draw_text(draw, (SAFE_X + 2, subline_y + 2), subline_text, 29, (0, 0, 0, 160), False, 10)
        draw_text(draw, (SAFE_X, subline_y), subline_text, 29, (255, 255, 255, 226), False, 10)


def feed_slide(topic: Topic, page: int) -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    add_photo_background(image, topic, page)
    draw_feed_gradient(image)
    draw = ImageDraw.Draw(image)
    label, headline, subline = case_slide_copy(topic, page)
    header(draw, topic, page, label)
    draw_feed_label(draw, label, page)
    draw_feed_headline(draw, headline, subline, page)
    if page == 5:
        draw_save_callout(draw)
    draw_cta(draw, page)
    footer(draw)
    draw.rectangle((0, 0, WIDTH - 1, HEIGHT - 1), outline=(8, 8, 8, 255), width=EDGE)
    draw_progress_bar(draw, page)
    return image.convert("RGB")


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


def instagram_caption_for(topic: Topic, target_date: date) -> str:
    hashtags = " ".join(INSTAGRAM_HASHTAGS)
    hook = INSTAGRAM_CAPTION_HOOKS.get(topic.slug, INSTAGRAM_DEFAULT_HOOK)
    return (
        f"{hook}\n\n"
        f"{topic.instagram}\n\n"
        f"{INSTAGRAM_OBSERVATION_LABEL}: {target_date.isoformat()}\n"
        f"{INSTAGRAM_SAVE_CRITERION}\n\n"
        f"{hashtags}"
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
    candidates = topic_photo_candidates(topic)
    if len(candidates) < MIN_UNIQUE_TOPIC_IMAGES:
        raise FileNotFoundError(
            f"Need at least {MIN_UNIQUE_TOPIC_IMAGES} unique image assets for topic slug "
            f"{topic.slug}; found {len(candidates)}. Run scripts/sync_topic_image_assets.py. "
            "Generic fallback backgrounds are not allowed for publishing."
        )


def load_disabled_pillars() -> set[str]:
    if not CONTENT_POLICY_PATH.exists():
        return set()
    payload = json.loads(CONTENT_POLICY_PATH.read_text(encoding="utf-8"))
    return {str(pillar).strip().casefold() for pillar in payload.get("disabled_pillars", []) if str(pillar).strip()}


def active_topics() -> tuple[Topic, ...]:
    disabled = load_disabled_pillars()
    topics = tuple(topic for topic in TOPICS if topic.pillar.casefold() not in disabled)
    if not topics:
        raise RuntimeError("No active topics available after applying content policy.")
    return topics


def create_package(target_date: date, out_root: Path) -> Path:
    topics = active_topics()
    index = (target_date - ANCHOR_DATE).days % len(topics)
    topic = topics[index]
    validate_topic_assets(topic)
    out = out_root / f"{target_date.isoformat()}-{topic.slug}"
    carousel = out / "carousel"
    instagram_carousel = out / "instagram-carousel"
    carousel.mkdir(parents=True, exist_ok=True)
    instagram_carousel.mkdir(parents=True, exist_ok=True)

    slides = [
        feed_slide(topic, 1),
        feed_slide(topic, 2),
        feed_slide(topic, 3),
        feed_slide(topic, 4),
        feed_slide(topic, 5),
    ]
    for page, image in enumerate(slides, start=1):
        image.save(carousel / f"{page:02d}.png", quality=95)
        image.convert("RGB").save(instagram_carousel / f"{page:02d}.jpg", quality=92, optimize=True)

    visual_assets = []
    asset_credits = topic_asset_credits(topic)
    for page in range(1, 6):
        source = topic_photo_source(topic, page)
        credit = asset_credits.get(source.name, {})
        visual_assets.append(
            {
                "page": page,
                "source": str(source.relative_to(ROOT) if source.is_relative_to(ROOT) else source),
                "provider": credit.get("provider", ""),
                "source_url": credit.get("source_url", ""),
                "query": credit.get("query", ""),
                "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            }
        )
    (out / "visual-source-manifest.json").write_text(
        json.dumps(
            {
                "engine": "bbbb.topic-image-priority.v1",
                "design_system": "bbbb.editorial-carousel.v2",
                "minimum_unique_sources": MIN_UNIQUE_TOPIC_IMAGES,
                "topic": topic.slug,
                "assets": visual_assets,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (out / "design-guide.json").write_text(
        json.dumps(
            {
                "system": "bbbb.editorial-carousel.v2",
                "reference": "editorial architecture/news carousel",
                "rules": [
                    "Full-bleed topic image, no decorative grid background.",
                    "Top-left BBBB wordmark and top-right page count on every slide.",
                    "Large section number on internal slides.",
                    "Dark bottom gradient for headline readability.",
                    "One strong hook headline in the lower third.",
                    "Bottom CTA and progress bar to encourage swiping and saving.",
                    "No provider/source label is printed on the image.",
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

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
