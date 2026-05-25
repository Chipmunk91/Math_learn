"""In-notebook AI tutor: a chapter-aware chat that each visitor powers with
their *own* Anthropic API key.

Why bring-your-own-key. The lesson is a static site served from GitHub Pages
and run in the browser via Pyodide. There is no server we control, and we do
not want to embed a shared key (that would bill *us* for every visitor). So the
visitor pastes their own Anthropic key into a password field; it lives only in
their browser for the session (kernel memory — gone on reload), and requests go
**directly** from their browser to ``api.anthropic.com`` using the documented
``anthropic-dangerous-direct-browser-access`` header. The key never reaches any
server of ours, and each visitor pays for their own usage.

Optional owner-pays mode. If you *do* want to foot the bill (e.g. a closed
classroom), pass ``endpoint=`` pointing at the Cloudflare Worker in ``worker/``;
then no key field is shown and the Worker's key is used instead.

Usage in a chapter::

    panel = delib.tutor(CHAPTER_CONTEXT, section="Try it", starters=[...])
    panel  # renders the key field + chat

The same widget works in a local ``marimo edit`` session, where the request
goes out through a plain blocking HTTP client run off the event loop.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Mapping, Sequence

import marimo as mo

__all__ = ["tutor", "TUTOR_ENDPOINT", "MODEL_CHOICES", "DEFAULT_MODEL"]

# Owner-pays Worker URL. Leave as-is to use bring-your-own-key (the default);
# set it (or pass endpoint=) only if you want to pay for all visitors.
TUTOR_ENDPOINT = ""

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
KEY_CONSOLE_URL = "https://console.anthropic.com/settings/keys"

# Cheapest capable model first; the visitor can switch.
DEFAULT_MODEL = "claude-haiku-4-5-20251001"
MODEL_CHOICES: dict[str, str] = {
    "Claude Haiku 4.5 — fast & cheap": "claude-haiku-4-5-20251001",
    "Claude Sonnet 4.6 — stronger": "claude-sonnet-4-6",
}

_RUNNING_IN_BROWSER = sys.platform == "emscripten"
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

_NEEDS_KEY = (
    "**Add your Anthropic API key above to start.** "
    f"Create one at <{KEY_CONSOLE_URL}>. It stays in your browser for this "
    "session only and is sent directly to Anthropic — never to this site."
)


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


async def _post(url: str, headers: dict, payload: dict) -> str:
    body = json.dumps(payload)
    if _RUNNING_IN_BROWSER:
        from pyodide.http import pyfetch  # available only inside Pyodide

        try:
            resp = await pyfetch(url, method="POST", headers=headers, body=body)
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
        req = urllib.request.Request(url, data=body.encode("utf-8"), headers=headers, method="POST")
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


async def _ask_anthropic(api_key: str, model: str, system: str, turns: list, max_tokens: int) -> str:
    # Direct browser -> Anthropic. The dangerous-direct-browser-access header is
    # what makes Anthropic emit CORS headers so the call is allowed from a page.
    headers = {
        "content-type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": ANTHROPIC_VERSION,
        "anthropic-dangerous-direct-browser-access": "true",
    }
    payload = {"model": model, "max_tokens": max_tokens, "system": system, "messages": turns}
    return await _post(ANTHROPIC_URL, headers, payload)


async def _ask_worker(endpoint: str, system: str, turns: list, max_tokens: int) -> str:
    headers = {"content-type": "application/json"}
    payload = {"system": system, "messages": turns, "max_tokens": max_tokens}
    return await _post(endpoint, headers, payload)


def _intro_md(section: str | None) -> "mo.Html":
    where = f" about **{section}**" if section else ""
    return mo.md(
        f"""
        ## Ask the tutor

        Stuck{where}, or want to check your reasoning? Ask below. The tutor
        knows this chapter — it nudges you with hints before handing over a
        full answer.
        """
    )


def _byok_help_md() -> "mo.Html":
    return mo.md(
        f"""
        <details>
          <summary>Powered by <strong>your</strong> Anthropic key — why?</summary>

        This site is static (no server), so it can't safely hold an API key.
        Paste your own key below: it's stored only in this browser tab for the
        session, sent **directly** to Anthropic, and never to this site. You pay
        only for what you use. Get a key at [Anthropic Console]({KEY_CONSOLE_URL}).
        </details>
        """
    )


def tutor(
    chapter_context: str,
    *,
    section: str | None = None,
    starters: Sequence[str] | None = None,
    models: Mapping[str, str] | None = None,
    endpoint: str | None = None,
    max_height: int | None = 420,
):
    """A chapter-aware AI chat the visitor powers with their own Anthropic key.

    Returns a renderable panel: a key field + model picker + chat. The chat is
    grounded in ``chapter_context`` (sent as the system prompt) and, if given,
    the current ``section``. ``starters`` become clickable suggested prompts.

    Pass ``endpoint`` (or set :data:`TUTOR_ENDPOINT`) to use the owner-pays
    Cloudflare Worker instead; then no key field is shown.
    """
    system = _system_prompt(chapter_context, section)
    use_worker = endpoint or TUTOR_ENDPOINT
    model_map = dict(models or MODEL_CHOICES)

    api_key = mo.ui.text(
        kind="password",
        placeholder="sk-ant-...",
        label="Your Anthropic API key",
        full_width=True,
    )
    default_label = next(
        (label for label, mid in model_map.items() if mid == DEFAULT_MODEL),
        next(iter(model_map)),
    )
    model_dd = mo.ui.dropdown(options=model_map, value=default_label, label="Model")

    async def _model(messages, config) -> str:
        turns = [
            {
                "role": "assistant" if m.role == "assistant" else "user",
                "content": m.content if isinstance(m.content, str) else str(m.content),
            }
            for m in messages
            if m.role in ("user", "assistant")
        ]
        max_tokens = min(int(getattr(config, "max_tokens", _MAX_TOKENS) or _MAX_TOKENS), _MAX_TOKENS)
        if use_worker:
            return await _ask_worker(str(use_worker), system, turns, max_tokens)
        key = (api_key.value or "").strip()
        if not key:
            return _NEEDS_KEY
        return await _ask_anthropic(key, model_dd.value or DEFAULT_MODEL, system, turns, max_tokens)

    chat = mo.ui.chat(
        _model,
        prompts=list(starters) if starters else None,
        max_height=max_height,
    )

    if use_worker:
        return mo.vstack([_intro_md(section), chat])
    return mo.vstack(
        [
            _intro_md(section),
            _byok_help_md(),
            mo.hstack([api_key, model_dd], widths=[3, 2], gap=0.5),
            chat,
        ]
    )
