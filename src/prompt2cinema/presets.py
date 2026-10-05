from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Preset:
    name: str
    width: int
    height: int
    fps: int
    bitrate: str
    notes: str


# Resolution + FPS tuned for perceived motion quality vs encode cost
PRESETS: dict[str, Preset] = {
    "720p": Preset("720p", 1280, 720, 30, "6M", "Preview / fast iteration"),
    "1080p": Preset("1080p", 1920, 1080, 30, "12M", "Default delivery"),
    "1080p60": Preset("1080p60", 1920, 1080, 60, "18M", "Smooth action"),
    "1440p": Preset("1440p", 2560, 1440, 30, "20M", "QHD"),
    "4k": Preset("4k", 3840, 2160, 30, "35M", "UHD cinematic"),
    "4k60": Preset("4k60", 3840, 2160, 60, "50M", "UHD smooth"),
    "8k": Preset("8k", 7680, 4320, 24, "80M", "Film-like ultra (heavy)"),
    "8k30": Preset("8k30", 7680, 4320, 30, "100M", "Ultra smooth (very heavy)"),
}


def get_preset(name: str) -> Preset:
    key = (name or "1080p").strip().lower().replace(" ", "")
    aliases = {
        "uhd": "4k",
        "2160p": "4k",
        "4320p": "8k",
        "hd": "1080p",
        "fhd": "1080p",
    }
    key = aliases.get(key, key)
    if key not in PRESETS:
        raise ValueError(f"Unknown preset {name!r}. Choose from: {', '.join(PRESETS)}")
    return PRESETS[key]


def optimized_fps(duration_s: float, preset: Preset, style: str = "cinematic") -> int:
    """Pick FPS based on style while respecting preset ceiling."""
    style = (style or "cinematic").lower()
    if style in {"film", "cinematic", "drama"}:
        target = 24
    elif style in {"action", "sports", "smooth"}:
        target = 60
    elif style in {"doc", "talking-head", "default"}:
        target = 30
    else:
        target = preset.fps
    # never exceed preset fps; bump down for very short clips to save work
    if duration_s < 2.0 and target > 30:
        target = 30
    return min(target, preset.fps)
