from prompt2cinema.presets import get_preset, optimized_fps
from prompt2cinema.planning.storyboard import plan_storyboard
from prompt2cinema.enhance.prompts import enhance_prompt


def test_presets_4k_8k():
    assert get_preset("4k").width == 3840
    assert get_preset("8k").height == 4320
    assert optimized_fps(6, get_preset("4k60"), "cinematic") == 24
    assert optimized_fps(6, get_preset("4k60"), "action") == 60


def test_enhance_and_plan():
    e = enhance_prompt("neon rain alley chase", offline=True)
    assert "neon" in e["enhanced"].lower() or "cinematic" in e["enhanced"].lower()
    board = plan_storyboard(e["enhanced"], duration_s=4, style="action")
    assert len(board.shots) >= 2
    assert any("rain" in " ".join(s.vfx) or "neon" in " ".join(s.vfx) for s in board.shots)
