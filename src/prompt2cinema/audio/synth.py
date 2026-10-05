from __future__ import annotations

import math
import struct
import wave
from pathlib import Path


def write_ambiance_wav(
    path: Path,
    *,
    duration_s: float,
    sample_rate: int = 44100,
    style: str = "cinematic",
) -> Path:
    """Synthesize a simple stereo ambience bed (no external TTS dependency)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    n = int(duration_s * sample_rate)
    style = (style or "cinematic").lower()

    def sample(i: int) -> float:
        t = i / sample_rate
        # layered tones
        if "action" in style:
            base = 0.18 * math.sin(2 * math.pi * 110 * t)
            pulse = 0.12 * math.sin(2 * math.pi * 2.5 * t) * math.sin(2 * math.pi * 220 * t)
        elif "space" in style or "dream" in style:
            base = 0.15 * math.sin(2 * math.pi * 82 * t)
            pulse = 0.1 * math.sin(2 * math.pi * 0.25 * t) * math.sin(2 * math.pi * 330 * t)
        else:
            base = 0.14 * math.sin(2 * math.pi * 98 * t)
            pulse = 0.08 * math.sin(2 * math.pi * 0.4 * t) * math.sin(2 * math.pi * 196 * t)
        # soft noise-ish shimmer via deterministic hash
        shimmer = 0.03 * math.sin(2 * math.pi * (1000 + (i % 97)) * t)
        env = min(1.0, t * 3) * min(1.0, max(0.0, duration_s - t) * 3)
        return max(-1.0, min(1.0, (base + pulse + shimmer) * env))

    with wave.open(str(path), "w") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = bytearray()
        for i in range(n):
            v = int(sample(i) * 30000)
            frames += struct.pack("<hh", v, int(v * 0.92))
        wf.writeframes(frames)
    return path
