from __future__ import annotations

import json
import shutil
from dataclasses import asdict, dataclass, field
from pathlib import Path

from prompt2cinema.audio.synth import write_ambiance_wav
from prompt2cinema.backends.cloud import try_cloud_generate
from prompt2cinema.backends.ffmpeg_backend import encode_frames_to_video, mux_audio
from prompt2cinema.enhance.prompts import enhance_prompt
from prompt2cinema.planning.storyboard import plan_storyboard
from prompt2cinema.presets import get_preset, optimized_fps
from prompt2cinema.vfx.effects import apply_vfx, render_base_frame


@dataclass
class CinemaRequest:
    prompt: str
    preset: str = "1080p"
    duration_s: float = 6.0
    style: str = "cinematic"
    offline: bool = True
    out_dir: Path = field(default_factory=lambda: Path("outputs"))
    keep_frames: bool = False


@dataclass
class CinemaResult:
    video_path: Path
    audio_path: Path
    storyboard_path: Path
    meta_path: Path
    width: int
    height: int
    fps: int
    duration_s: float
    enhanced_prompt: str


def generate_cinema(req: CinemaRequest) -> CinemaResult:
    preset = get_preset(req.preset)
    fps = optimized_fps(req.duration_s, preset, req.style)
    enhance = enhance_prompt(req.prompt, offline=req.offline)
    board = plan_storyboard(enhance["enhanced"], duration_s=req.duration_s, style=req.style)

    work = Path(req.out_dir) / "job"
    if work.exists():
        shutil.rmtree(work)
    frames_dir = work / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    # Prefer cloud if configured; always have local fallback
    cloud = try_cloud_generate(
        enhance["enhanced"],
        width=preset.width,
        height=preset.height,
        fps=fps,
        duration_s=board.total_duration_s,
    )

    frame_idx = 0
    # For huge 8K, optionally render lower then upscale — still honor request dims at encode
    render_w, render_h = preset.width, preset.height
    if preset.name.startswith("8k") and req.offline:
        # generate at 4K then lanczos upscale in ffmpeg for speed
        render_w, render_h = 3840, 2160

    for shot in board.shots:
        n_frames = max(1, int(round(shot.duration_s * fps)))
        for i in range(n_frames):
            t = i / fps
            base = render_base_frame(
                render_w,
                render_h,
                prompt=enhance["enhanced"],
                shot_label=f"Shot {shot.index}: {shot.camera}",
                t=t,
                duration=shot.duration_s,
            )
            framed = apply_vfx(base, shot.vfx + ["color_grade", "film_grain"], t=t, frame_idx=frame_idx)
            framed.save(frames_dir / f"frame_{frame_idx:06d}.png")
            frame_idx += 1

    silent = work / "silent.mp4"
    pattern = str(frames_dir / "frame_%06d.png")
    encode_frames_to_video(
        pattern,
        silent,
        fps=fps,
        bitrate=preset.bitrate,
        width=preset.width,
        height=preset.height,
    )

    audio = work / "ambiance.wav"
    write_ambiance_wav(audio, duration_s=board.total_duration_s, style=req.style)

    final = Path(req.out_dir) / f"cinema_{preset.name}_{fps}fps.mp4"
    mux_audio(silent, audio, final)

    storyboard_path = Path(req.out_dir) / "storyboard.json"
    meta_path = Path(req.out_dir) / "meta.json"
    storyboard_path.write_text(json.dumps(board.to_dict(), indent=2), encoding="utf-8")
    meta = {
        "request": {
            "prompt": req.prompt,
            "preset": req.preset,
            "duration_s": req.duration_s,
            "style": req.style,
            "offline": req.offline,
        },
        "enhance": enhance,
        "cloud": asdict(cloud),
        "output": {
            "width": preset.width,
            "height": preset.height,
            "fps": fps,
            "frames": frame_idx,
            "video": str(final),
        },
        "notes": (
            "Local renderer is a procedural cinematic stand-in for diffusion T2V. "
            "Plug a real VIDEO_API provider for photoreal model output."
        ),
    }
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    if not req.keep_frames:
        shutil.rmtree(frames_dir, ignore_errors=True)

    return CinemaResult(
        video_path=final,
        audio_path=audio,
        storyboard_path=storyboard_path,
        meta_path=meta_path,
        width=preset.width,
        height=preset.height,
        fps=fps,
        duration_s=board.total_duration_s,
        enhanced_prompt=enhance["enhanced"],
    )
