# prompt2cinema

**Text → cinematic video + audio + VFX**  
Resolution presets from **720p → 8K**, FPS optimized by style (24 / 30 / 60).

Interview- and startup-ready open-source pipeline that combines techniques from
agentic planning, LLM prompt enhancement, generative rendering, and optional
cloud T2V backends.

[![CI](https://github.com/balasahu87/prompt2cinema/actions/workflows/ci.yml/badge.svg)](https://github.com/balasahu87/prompt2cinema/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What it does

```text
Text prompt
   │
   ├─ Prompt enhancement (multi-variant + critique / offline polish)
   ├─ Agentic storyboard (shots, camera, audio, VFX tags)
   ├─ Frame render + VFX (grain, rain, fog, neon glow, bloom, …)
   ├─ Ambience audio bed
   └─ ffmpeg mux → MP4 at chosen preset (720p / 1080p / 4K / 8K …)
```

| Capability | Implementation in v0.1 |
|------------|------------------------|
| Prompt enhancement | Offline cinematic polish; optional OpenAI-compatible API |
| Shot planning | Deterministic agentic storyboard |
| Video | Local procedural cinematic renderer (photoreal T2V via `VIDEO_API_*` stub) |
| Audio | Synthesized stereo ambience → AAC |
| VFX | rain, fog, neon glow, film grain, starfield, flash bloom, color grade |
| Resolution | `720p`, `1080p`, `1080p60`, `1440p`, `4k`, `4k60`, `8k`, `8k30` |
| FPS | Auto: cinematic→24, default→30, action→60 (capped by preset) |

> **Honest scope:** True diffusion/transformer text-to-video models need large GPUs or paid APIs.
> This repo ships a **complete local pipeline** you can run today, plus a clean hook to plug
> Runway / fal / Replicate / Kling-style providers when you have keys.

---

## Quick start (local)

### Requirements

- Python **3.10+**
- ~1 GB free disk for venv + ffmpeg binary (auto-downloaded via `imageio-ffmpeg`)
- No system `ffmpeg` install required

### Install

```bash
git clone https://github.com/balasahu87/prompt2cinema.git
cd prompt2cinema

python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -U pip
pip install -e ".[dev]"
```

### List presets

```bash
prompt2cinema --list-presets
```

### Generate a clip (offline, recommended first run)

```bash
# Fast smoke (720p, ~3s)
prompt2cinema "neon cyberpunk street in the rain at night" \
  --preset 720p --duration 3 --style cinematic --out outputs/demo

# Open the file
open outputs/demo/cinema_720p_24fps.mp4   # macOS
# xdg-open outputs/demo/...               # Linux
```

### Higher resolution

```bash
# 1080p60 action
prompt2cinema "drone chase through mountain canyon" \
  --preset 1080p60 --duration 5 --style action --out outputs/action

# 4K cinematic (heavier)
prompt2cinema "solo astronaut on a misty alien shore at golden hour" \
  --preset 4k --duration 4 --style cinematic --out outputs/uhd

# 8K (renders internally at 4K then lanczos-upscales — still heavy)
prompt2cinema "vast orbital city above Earth, volumetric sunlight" \
  --preset 8k --duration 3 --style space --out outputs/8k
```

### Online prompt enhancement (optional)

```bash
cp .env.example .env
# set OPENAI_API_KEY=...
prompt2cinema "quiet library in the rain" --preset 1080p --online --out outputs/online
```

---

## Test locally

```bash
# Unit + integration (short 720p render)
pytest -q

# Full smoke script
bash scripts/smoke_test.sh
```

Expected: `outputs/smoke/cinema_720p_24fps.mp4` plus `storyboard.json` and `meta.json`.

---

## Project layout

```text
src/prompt2cinema/
  enhance/       # LLM / heuristic prompt upgrade
  planning/      # storyboard + shot agent
  vfx/           # visual effects
  audio/         # ambience synth
  backends/      # ffmpeg encode + cloud T2V stub
  pipeline.py    # end-to-end orchestration
  cli.py
```

---

## Cloud T2V hook

Set in `.env`:

```bash
VIDEO_API_KEY=...
VIDEO_API_BASE=https://your-provider.example/v1
```

Then implement the provider call in [`src/prompt2cinema/backends/cloud.py`](src/prompt2cinema/backends/cloud.py).
Until then, the local renderer always runs so demos stay reproducible.

---

## Interview / startup talking points

1. **Systems design** — prompt → plan → render → mux, with budgets (duration, preset, fps).
2. **LLM techniques** — multi-variant prompts + critique-revise (same family as llmboost).
3. **Agentic planning** — shot list with camera/audio/VFX intents before pixels.
4. **Production realism** — presets, bitrate, upscale path for 8K, CI smoke renders.
5. **Extensibility** — swap procedural frames for a real T2V API without changing the CLI.

---

## License

MIT — see [LICENSE](LICENSE).
