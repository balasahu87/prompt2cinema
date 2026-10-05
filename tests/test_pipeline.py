from pathlib import Path

from prompt2cinema.pipeline import CinemaRequest, generate_cinema


def test_generate_short_720p(tmp_path: Path):
    result = generate_cinema(
        CinemaRequest(
            prompt="foggy mountain sunrise with soft mist",
            preset="720p",
            duration_s=2.0,
            style="cinematic",
            offline=True,
            out_dir=tmp_path / "out",
            keep_frames=False,
        )
    )
    assert result.video_path.exists()
    assert result.video_path.stat().st_size > 1000
    assert result.width == 1280
    assert result.height == 720
    assert result.fps == 24  # cinematic style
    assert result.storyboard_path.exists()
