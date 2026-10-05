from __future__ import annotations

import os
import re
from typing import Protocol


class LLMClient(Protocol):
    def complete(self, prompt: str) -> str: ...


class EchoEnhancer:
    """Offline prompt enhancer (no API)."""

    def complete(self, prompt: str) -> str:
        return prompt


class OpenAICompatClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY") or ""
        self.base = (os.getenv("OPENAI_API_BASE") or "https://api.openai.com/v1").rstrip("/")
        self.model = os.getenv("OPENAI_MODEL") or "gpt-4o-mini"

    def complete(self, prompt: str) -> str:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY missing")
        import json
        import urllib.request

        body = json.dumps(
            {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.4,
            }
        ).encode()
        req = urllib.request.Request(
            f"{self.base}/chat/completions",
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
        return data["choices"][0]["message"]["content"]


def expand_queries(llm: LLMClient, prompt: str, n: int = 3) -> list[str]:
    raw = llm.complete(
        f"Rewrite this cinematic video prompt into {n} richer variations, one per line.\n\n{prompt}"
    )
    lines = [re.sub(r"^[\d\-\*\.]+\s*", "", ln).strip() for ln in raw.splitlines() if ln.strip()]
    out = [prompt]
    for ln in lines:
        if ln and ln.lower() != prompt.lower() and ln not in out:
            out.append(ln)
        if len(out) >= n + 1:
            break
    while len(out) < n + 1:
        out.append(f"{prompt}, cinematic lighting variation {len(out)}")
    return out[: n + 1]


def critique_revise(llm: LLMClient, prompt: str) -> str:
    critique = llm.complete(
        "Critique this video prompt for realism, camera language, lighting, audio cues, "
        f"and VFX clarity. List gaps briefly.\n\n{prompt}"
    )
    revised = llm.complete(
        "Revise the video prompt using the critique. Return only the improved prompt.\n"
        f"Original:\n{prompt}\nCritique:\n{critique}"
    )
    return revised.strip() or prompt


def enhance_prompt(prompt: str, *, offline: bool = True) -> dict:
    """
    Apply llmboost-style techniques:
    multi-query expansion + critique-revise (online) or heuristic polish (offline).
    """
    prompt = (prompt or "").strip()
    if not prompt:
        raise ValueError("empty prompt")

    if offline or not os.getenv("OPENAI_API_KEY"):
        polished = (
            f"{prompt}. Photorealistic, cinematic color grade, detailed textures, "
            "natural motion, coherent lighting, subtle film grain, immersive ambience."
        )
        variants = [
            polished,
            f"{prompt}, golden-hour volumetric light, shallow depth of field, 35mm lens",
            f"{prompt}, dramatic contrast, anamorphic bokeh, atmospheric fog, IMAX scale",
        ]
        return {
            "original": prompt,
            "enhanced": polished,
            "variants": variants,
            "mode": "offline-heuristic",
        }

    llm = OpenAICompatClient()
    variants = expand_queries(llm, prompt, n=3)
    best = critique_revise(llm, variants[0])
    return {
        "original": prompt,
        "enhanced": best,
        "variants": variants,
        "mode": "online-llmboost",
    }
