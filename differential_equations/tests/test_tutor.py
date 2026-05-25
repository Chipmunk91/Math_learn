"""Tests for the AI tutor's pure logic (prompt building + response parsing).

No network: we never call the Worker here. Those paths are exercised live in
the browser / a local marimo session.
"""

import delib
from delib.tutor import (
    DEFAULT_MODEL,
    MODEL_CHOICES,
    _extract_text,
    _system_prompt,
)


def test_system_prompt_embeds_chapter_and_section():
    prompt = _system_prompt("Logistic: y' = a*y*(1 - y/K).", section="Try it")
    assert "Logistic: y' = a*y*(1 - y/K)." in prompt
    assert "Try it" in prompt
    # The pedagogical guardrail (hints before answers) is always present.
    assert "hint" in prompt.lower()


def test_system_prompt_without_section():
    prompt = _system_prompt("Some chapter text.", section=None)
    assert "Some chapter text." in prompt
    assert "currently working through the section" not in prompt


def test_extract_text_from_anthropic_content():
    data = {"content": [{"type": "text", "text": "Hello"}, {"type": "text", "text": ", world"}]}
    assert _extract_text(data) == "Hello, world"


def test_extract_text_ignores_non_text_blocks():
    data = {"content": [{"type": "thinking", "text": "hmm"}, {"type": "text", "text": "answer"}]}
    assert _extract_text(data) == "answer"


def test_extract_text_surfaces_error_message():
    data = {"error": {"type": "overloaded_error", "message": "Overloaded"}}
    assert "Overloaded" in _extract_text(data)
    assert _extract_text(data).startswith("⚠️")


def test_extract_text_handles_unexpected_shape():
    assert _extract_text(["not", "a", "dict"]).startswith("⚠️")


def test_default_model_is_an_offered_choice():
    assert DEFAULT_MODEL in MODEL_CHOICES.values()


def test_tutor_builds_in_both_modes():
    # Bring-your-own-key (default) and owner-pays Worker both produce a panel.
    byok = delib.tutor("ctx", section="Try it", starters=["hi"])
    owner = delib.tutor("ctx", endpoint="https://example.workers.dev")
    for panel in (byok, owner):
        assert hasattr(panel, "text")  # a marimo renderable

    # BYOK shows the key field; owner-pays mode hides it.
    assert "password" in byok.text
    assert "password" not in owner.text
