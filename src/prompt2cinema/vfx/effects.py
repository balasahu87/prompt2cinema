from __future__ import annotations

import math
import random
from typing import Iterable

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter


def _hash_color(text: str) -> tuple[int, int, int]:
    h = abs(hash(text))
    r = 40 + (h & 127)
    g = 40 + ((h >> 8) & 127)
    b = 40 + ((h >> 16) & 127)
    return r, g, b


def render_base_frame(
    width: int,
    height: int,
    *,
    prompt: str,
    shot_label: str,
    t: float,
    duration: float,
) -> Image.Image:
    """Procedural cinematic frame (offline stand-in for diffusion T2V)."""
    c1 = _hash_color(prompt)
    c2 = _hash_color(prompt[::-1] + shot_label)
    img = Image.new("RGB", (width, height), c1)
    draw = ImageDraw.Draw(img, "RGBA")

    # moving gradient orbs
    phase = (t / max(duration, 0.001)) * math.pi * 2
    for i in range(5):
        cx = int(width * (0.2 + 0.15 * i) + math.sin(phase + i) * width * 0.08)
        cy = int(height * (0.35 + 0.1 * math.cos(phase * 1.3 + i)))
        rad = int(min(width, height) * (0.18 + 0.03 * i))
        color = (*c2, 90)
        draw.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=color)

    # horizon band
    y0 = int(height * (0.55 + 0.05 * math.sin(phase)))
    draw.rectangle((0, y0, width, height), fill=(*c1, 180))

    # title card text
    label = (shot_label[:80] + "…") if len(shot_label) > 80 else shot_label
    # scale font roughly with resolution
    try:
        from PIL import ImageFont

        size = max(18, width // 40)
        font = ImageFont.load_default()
        # default font is small; draw thicker via multiple passes
        tx, ty = width // 12, height // 10
        for dx, dy in ((0, 0), (1, 0), (0, 1)):
            draw.text((tx + dx, ty + dy), label, fill=(240, 240, 245, 230), font=font)
        draw.text((tx, ty + size), prompt[:100], fill=(210, 210, 220, 200), font=font)
    except Exception:
        draw.text((40, 40), label, fill=(240, 240, 245, 230))

    return img.convert("RGB")


def apply_vfx(img: Image.Image, effects: Iterable[str], *, t: float, frame_idx: int) -> Image.Image:
    effects = list(effects or [])
    out = img

    if "color_grade" in effects:
        out = ImageEnhance.Color(out).enhance(1.25)
        out = ImageEnhance.Contrast(out).enhance(1.15)

    if "soft_glow" in effects or "neon_glow" in effects:
        blur = out.filter(ImageFilter.GaussianBlur(radius=max(1, out.width // 400)))
        out = Image.blend(out, blur, 0.35 if "neon_glow" in effects else 0.22)

    if "fog_haze" in effects:
        fog = Image.new("RGB", out.size, (180, 190, 200))
        out = Image.blend(out, fog, 0.18)

    if "film_grain" in effects:
        # light deterministic grain
        rng = random.Random(frame_idx * 9973)
        px = out.load()
        w, h = out.size
        step = max(1, w // 480)
        for y in range(0, h, step):
            for x in range(0, w, step):
                n = rng.randint(-12, 12)
                r, g, b = px[x, y]
                px[x, y] = (max(0, min(255, r + n)), max(0, min(255, g + n)), max(0, min(255, b + n)))

    if "rain_overlay" in effects:
        draw = ImageDraw.Draw(out)
        rng = random.Random(frame_idx + 42)
        for _ in range(max(40, out.width // 30)):
            x = rng.randint(0, out.width)
            y = rng.randint(0, out.height)
            draw.line((x, y, x - 3, y + 18), fill=(200, 210, 230), width=1)

    if "starfield" in effects:
        draw = ImageDraw.Draw(out)
        rng = random.Random(7)
        for _ in range(max(80, out.width // 20)):
            x = rng.randint(0, out.width - 1)
            y = rng.randint(0, int(out.height * 0.55))
            draw.point((x, y), fill=(255, 255, 255))

    if "flash_bloom" in effects and (t % 1.7) < 0.08:
        flash = Image.new("RGB", out.size, (255, 255, 255))
        out = Image.blend(out, flash, 0.35)

    if "motion_blur" in effects:
        out = out.filter(ImageFilter.GaussianBlur(radius=1.2))

    return out
