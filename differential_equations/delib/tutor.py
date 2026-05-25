"""In-notebook AI tutor: a chapter-aware chat backed by a Claude proxy.

The chat widget runs inside the browser (Pyodide) on the static GitHub Pages
site, so it cannot talk to Anthropic directly: Anthropic's API blocks
cross-origin browser calls, and an API key must never ship inside static
files. Instead the widget POSTs to a small Cloudflare Worker (see ``worker/``)
that holds the key server-side and forwards the request. The exact same widget
also works in a local ``marimo edit`` session, where it falls back to a plain
blocking HTTP client run off the event loop.

Usage in a chapter::

    tutor_chat = delib.tutor(
        CHAPTER_CONTEXT,
        section="Try it",
        starters=["Check my answer to question 1: ..."],
    )
    mo.vstack([mo.md("## Ask the tutor"), tutor_chat])
"""

from __future__ import annotations

import json
import sys
from collections.abc import Sequence

import marimo as mo

__all__ = ["tutor", "TUTOR_ENDPOINT"]

# Deploy ``worker/`` and paste its public URL here, or pass ``endpoint=`` to
# :func:`tutor`. Until this points at a real Worker the widget will report a
# connection error when asked a question.
TUTOR_ENDPOINT = "https://math-tutor.example.workers.dev"

_RUNNING_IN_BROWSER = sys.platform == "emscripten"

# Keep replies short and cheap; the Worker clamps this too.
_MAX_TOKENS = 800

_TUTOR_GUIDE = """\
You are a patient, Socratic tutor embedded directly inside an interactive \
differential-equations lesson. The learner is reading the chapter below and \
experimenting with live sliders and animations as they ask you questions.

How to help:
- Teach through guidance, not answer dumps. When the learner is stuck, offer \
the next hint or a guiding question first; reveal a full solution only after \
they have tried, or if they explicitly ask for it.
- When they propose an answer, give specific feedback: say what is right, \
pinpoint exactly where any reasoning breaks, and nudge them to the fix.
- Stay anchored to THIS chapter's equation, parameters, and figures. Connect \
your explanations to what they can see on screen (the slope field, the red \
solution curve, the equilibria).
- Be concise and encouraging. Prefer a few focused sentences over a wall of \
text. Use Markdown, and write math with $...$ / $$...$$ (it renders as KaTeX).
- If a question is unrelated to the chapter, answer briefly and steer back."""


def _system_prompt(chapter: str, section: str | None) -> str:
    here = (
        f"\nThe learner is currently working through the section **{section}**.\n"
        if section
        else "\n"
    )
    return (
        f"{_TUTOR_GUIDE}\n{here}\n"
        "## The chapter the learner is studying\n\n"
        f"{chapter.strip()}\n"
    )


def _extract_text(data: object) -> str:
    """Pull the assistant text out of an Anthropic Messages response (or error)."""
    if isinstance(data, dict):
        content = data.get("content")
        if isinstance(content, list):
            text = "".join(
                block.get("text", "")
                for block in content
                if isinstance(block, dict) and block.get("type") == "text"
            )
            return text or "_(The tutor returned an empty response.)_"
        if "error" in data:
            err = data["error"]
            message = err.get("message") if isinstance(err, dict) else err
            return f"⚠️ Tutor error: {message}"
    return "⚠️ Unexpected response from the tutor service."


async def _post(endpoint: str, payload: dict) -> str:
    body = json.dumps(payload)
    headers = {"Content-Type": "application/json"}
    if _RUNNING_IN_BROWSER:
        from pyodide.http import pyfetch  # available only inside Pyodide

        try:
            resp = await pyfetch(endpoint, method="POST", headers=headers, body=body)
        except Exception as exc:  # network / CORS failure
            return f"⚠️ Could not reach the tutor service: {exc}"
        try:
            data = await resp.json()
        except Exception:
            return f"⚠️ Tutor returned a non-JSON response (HTTP {resp.status})."
        return _extract_text(data)

    import asyncio
    import urllib.error
    import urllib.request

    def _blocking() -> object:
        req = urllib.request.Request(
            endpoint, data=body.encode("utf-8"), headers=headers, method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            try:
                return json.loads(exc.read().decode("utf-8"))
            except Exception:
                return {"error": {"message": f"HTTP {exc.code}"}}
        except Exception as exc:
            return {"error": {"message": str(exc)}}

    data = await asyncio.to_thread(_blocking)
    return _extract_text(data)


def tutor(
    chapter_context: str,
    *,
    section: str | None = None,
    starters: Sequence[str] | None = None,
    endpoint: str | None = None,
    max_height: int | None = 420,
):
    """A chapter-aware AI chat widget (:func:`marimo.ui.chat`).

    ``chapter_context`` is plain text describing the chapter — its equation,
    parameters, key ideas, and exercises. It is sent as the system prompt so
    the tutor's help is grounded in exactly what the learner is reading.

    ``section`` optionally tells the tutor which part of the chapter the
    learner is on. ``starters`` become clickable suggested prompts. ``endpoint``
    overrides :data:`TUTOR_ENDPOINT` (the Worker URL).
    """
    target = endpoint or TUTOR_ENDPOINT
    system = _system_prompt(chapter_context, section)

    async def _model(messages, config) -> str:
        max_tokens = min(int(getattr(config, "max_tokens", _MAX_TOKENS) or _MAX_TOKENS), _MAX_TOKENS)
        turns = [
            {
                "role": "assistant" if m.role == "assistant" else "user",
                "content": m.content if isinstance(m.content, str) else str(m.content),
            }
            for m in messages
            if m.role in ("user", "assistant")
        ]
        return await _post(target, {"system": system, "messages": turns, "max_tokens": max_tokens})

    return mo.ui.chat(
        _model,
        prompts=list(starters) if starters else None,
        max_height=max_height,
    )
