from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass


@dataclass
class Shot:
    index: int
    duration_s: float
    visual: str
    camera: str
    audio: str
    vfx: list[str]


@dataclass
class Storyboard:
    title: str
    style: str
    total_duration_s: float
    shots: list[Shot]

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "style": self.style,
            "total_duration_s": self.total_duration_s,
            "shots": [asdict(s) for s in self.shots],
        }


_VFX_KEYWORDS = {
    "rain": "rain_overlay",
    "storm": "rain_overlay",
    "neon": "neon_glow",
    "night": "neon_glow",
    "fog": "fog_haze",
    "mist": "fog_haze",
    "explosion": "flash_bloom",
    "fire": "flash_bloom",
    "space": "starfield",
    "galaxy": "starfield",
    "slow": "motion_blur",
    "dream": "soft_glow",
}


def plan_storyboard(enhanced_prompt: str, *, duration_s: float = 6.0, style: str = "cinematic") -> Storyboard:
    """
    Agentic-style shot planner (deterministic offline).
    Splits a prompt into timed shots with camera / audio / VFX intents.
    """
    duration_s = max(2.0, min(float(duration_s), 60.0))
    # 2–5 shots depending on length
    n = 2 if duration_s < 4 else 3 if duration_s < 10 else 4 if duration_s < 20 else 5
    per = duration_s / n
    tokens = re.findall(r"[a-zA-Z0-9']+", enhanced_prompt.lower())
    vfx = sorted({v for k, v in _VFX_KEYWORDS.items() if k in tokens}) or ["film_grain", "color_grade"]

    cameras = [
        "wide establishing, slow push-in",
        "medium tracking shot",
        "close-up detail, shallow DOF",
        "orbiting crane move",
        "handheld documentary follow",
    ]
    audio_beds = [
        "ambient bed + soft pads",
        "rhythmic pulse + foley",
        "orchestral swell",
        "tense drones",
        "airy whoosh transitions",
    ]

    digest = hashlib.sha1(enhanced_prompt.encode()).hexdigest()
    title = " ".join(enhanced_prompt.split()[:8]).strip(".,") or "Untitled"
    shots: list[Shot] = []
    for i in range(n):
        seed = int(digest[i * 2 : i * 2 + 2], 16)
        shots.append(
            Shot(
                index=i + 1,
                duration_s=round(per, 3),
                visual=f"{enhanced_prompt} — beat {i+1}/{n}",
                camera=cameras[(seed + i) % len(cameras)],
                audio=audio_beds[(seed + i * 3) % len(audio_beds)],
                vfx=vfx if i == 0 else vfx[:2] + (["flash_bloom"] if i == n - 1 and "flash_bloom" in vfx else []),
            )
        )
    return Storyboard(title=title, style=style, total_duration_s=duration_s, shots=shots)
