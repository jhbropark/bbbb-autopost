"""Build a vertical Instagram Reels MP4 from the daily carousel images."""

from __future__ import annotations

import argparse
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

WIDTH = 1080
HEIGHT = 1920
FPS = 24


def fit_cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return ImageOpsFit.cover(image.convert("RGB"), size)


class ImageOpsFit:
    @staticmethod
    def cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
        src_w, src_h = image.size
        dst_w, dst_h = size
        scale = max(dst_w / src_w, dst_h / src_h)
        new_size = (round(src_w * scale), round(src_h * scale))
        resized = image.resize(new_size, Image.Resampling.LANCZOS)
        left = (new_size[0] - dst_w) // 2
        top = (new_size[1] - dst_h) // 2
        return resized.crop((left, top, left + dst_w, top + dst_h))


def compose_frame(source: Image.Image, progress: float, slide_index: int, slide_count: int) -> np.ndarray:
    source = source.convert("RGB")
    scale = 1.0 + progress * 0.035
    scaled = source.resize((round(source.width * scale), round(source.height * scale)), Image.Resampling.LANCZOS)
    left = (scaled.width - source.width) // 2
    top = (scaled.height - source.height) // 2
    card = scaled.crop((left, top, left + source.width, top + source.height))

    background = fit_cover(card, (WIDTH, HEIGHT)).filter(ImageFilter.GaussianBlur(28))
    shade = Image.new("RGBA", (WIDTH, HEIGHT), (10, 16, 27, 122))
    canvas = Image.alpha_composite(background.convert("RGBA"), shade)

    card_w = 980
    card_h = 980
    card = card.resize((card_w, card_h), Image.Resampling.LANCZOS).convert("RGBA")
    x = (WIDTH - card_w) // 2
    y = 420
    canvas.alpha_composite(card, (x, y))

    draw = ImageDraw.Draw(canvas)
    draw.text((50, 68), "bbbb / MEDICAL ANIMATION", fill=(255, 255, 255, 225))
    draw.text((WIDTH - 140, 68), f"{slide_index:02d}/{slide_count:02d}", fill=(14, 165, 233, 235))
    draw.text((50, HEIGHT - 116), "BBBB BEAUTY INTELLIGENCE", fill=(255, 255, 255, 205))
    return np.asarray(canvas.convert("RGB"))


def write_video(images: list[Path], out: Path, seconds_each: float) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    writer = imageio_ffmpeg.write_frames(
        str(out),
        (WIDTH, HEIGHT),
        fps=FPS,
        codec="libx264",
        pix_fmt_out="yuv420p",
        macro_block_size=1,
        output_params=["-movflags", "+faststart", "-crf", "20", "-preset", "medium"],
    )
    writer.send(None)
    try:
        frames_per_slide = max(1, round(seconds_each * FPS))
        slide_count = len(images)
        for slide_index, path in enumerate(images, start=1):
            image = Image.open(path)
            for frame_index in range(frames_per_slide):
                progress = frame_index / max(1, frames_per_slide - 1)
                writer.send(compose_frame(image, progress, slide_index, slide_count).tobytes())
    finally:
        writer.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--carousel-dir", required=True, type=Path)
    parser.add_argument("--instagram-caption", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--caption-out", required=True, type=Path)
    parser.add_argument("--seconds-each", type=float, default=2.4)
    args = parser.parse_args()

    images = sorted(args.carousel_dir.glob("*.png"))
    if not images:
        raise SystemExit(f"No PNG images found in {args.carousel_dir}")
    write_video(images, args.out, args.seconds_each)

    base_caption = args.instagram_caption.read_text(encoding="utf-8").strip()
    reel_caption = f"{base_caption}\n\nReels format: mechanism in motion."
    args.caption_out.write_text(reel_caption, encoding="utf-8")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
