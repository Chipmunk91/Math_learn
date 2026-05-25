"""Tests for the AI tutor's pure logic (prompt building + response parsing).

No network: we never call the Worker here. Those paths are exercised live in
the browser / a local marimo session.
"""

from delib.tutor import _extract_text, _system_prompt


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
