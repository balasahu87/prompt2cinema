"""Optional cloud T2V backend stubs (wired for future API keys)."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class CloudJob:
    ok: bool
    message: str
    video_url: str | None = None


def try_cloud_generate(prompt: str, *, width: int, height: int, fps: int, duration_s: float) -> CloudJob:
    """
    Placeholder for Runway / fal / Replicate / Kling style APIs.
    Returns not-configured unless VIDEO_API_KEY is set (still stubbed in v0.1).
    """
    key = os.getenv("VIDEO_API_KEY")
    if not key:
        return CloudJob(False, "VIDEO_API_KEY not set — using local procedural renderer")
    # Intentionally stubbed: document how to plug a real provider
    return CloudJob(
        False,
        (
            "Cloud backend stub: set VIDEO_API_BASE and implement providers in "
            "backends/cloud.py for production T2V. Falling back to local renderer."
        ),
    )
