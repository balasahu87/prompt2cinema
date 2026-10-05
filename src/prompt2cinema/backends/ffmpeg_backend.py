from __future__ import annotations

import subprocess
from pathlib import Path

import imageio_ffmpeg


def ffmpeg_exe() -> str:
    return imageio_ffmpeg.get_ffmpeg_exe()


def encode_frames_to_video(
    frame_pattern: str,
    out_video: Path,
    *,
    fps: int,
    bitrate: str,
    width: int,
    height: int,
) -> Path:
    """Encode PNG sequence → H.264 MP4 via bundled ffmpeg."""
    out_video.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg_exe(),
        "-y",
        "-framerate",
        str(fps),
        "-i",
        frame_pattern,
        "-vf",
        f"scale={width}:{height}:flags=lanczos",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-b:v",
        bitrate,
        "-movflags",
        "+faststart",
        str(out_video),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg encode failed:\n{proc.stderr[-2000:]}")
    return out_video


def mux_audio(video: Path, audio: Path, out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg_exe(),
        "-y",
        "-i",
        str(video),
        "-i",
        str(audio),
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-shortest",
        str(out),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg mux failed:\n{proc.stderr[-2000:]}")
    return out
