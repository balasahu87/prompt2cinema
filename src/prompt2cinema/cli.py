from __future__ import annotations

import argparse
from pathlib import Path

from prompt2cinema.pipeline import CinemaRequest, generate_cinema
from prompt2cinema.presets import PRESETS


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(
        prog="prompt2cinema",
        description="Generate cinematic video+audio+VFX from a text prompt (720p–8K presets)",
    )
    p.add_argument("prompt", nargs="?", help="Text prompt for the video")
    p.add_argument("--preset", default="720p", help=f"One of: {', '.join(PRESETS)}")
    p.add_argument("--duration", type=float, default=4.0, help="Duration seconds (2–60)")
    p.add_argument("--style", default="cinematic", help="cinematic|action|space|dream|...")
    p.add_argument("--out", type=Path, default=Path("outputs"))
    p.add_argument("--online", action="store_true", help="Use OPENAI_API_KEY for prompt enhancement")
    p.add_argument("--keep-frames", action="store_true")
    p.add_argument("--list-presets", action="store_true")
    args = p.parse_args(argv)

    if args.list_presets:
        for name, pr in PRESETS.items():
            print(f"{name:8} {pr.width}x{pr.height} @ up to {pr.fps}fps  ({pr.notes})")
        return

    if not args.prompt:
        raise SystemExit("Provide a prompt, or use --list-presets")

    result = generate_cinema(
        CinemaRequest(
            prompt=args.prompt,
            preset=args.preset,
            duration_s=args.duration,
            style=args.style,
            offline=not args.online,
            out_dir=args.out,
            keep_frames=args.keep_frames,
        )
    )
    print("enhanced:", result.enhanced_prompt[:200])
    print(f"video: {result.video_path} ({result.width}x{result.height} @ {result.fps}fps)")
    print(f"audio: {result.audio_path}")
    print(f"storyboard: {result.storyboard_path}")
    print(f"meta: {result.meta_path}")


if __name__ == "__main__":
    main()
