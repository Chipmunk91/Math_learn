"""Tests for the WASM site build: chapter discovery and navigation bar."""

import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _load_build_module():
    spec = importlib.util.spec_from_file_location(
        "build_wasm_site", REPO / "scripts" / "build_wasm_site.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


build = _load_build_module()


def test_chapters_only_includes_real_chapters():
    """Published chapters are chNN_<topic>.py; spikes and the template are skipped."""
    names = [p.name for p in build.chapters()]
    assert names, "expected at least one chapter"
    assert all(p.startswith("ch") and p[2:4].isdigit() for p in names)
    assert "_template.py" not in names
    assert not any(n.startswith("zz_spike") for n in names)


def test_nav_bar_disables_previous_on_first_chapter():
    names = ["ch01_a", "ch02_b", "ch03_c"]
    html = build.nav_bar(names, 0)
    assert "ml-nav-disabled" in html and "&larr; Previous" in html
    assert '<a href="../ch01_a/"' not in html
    assert '<a href="../ch02_b/"' in html  # Next links to the second chapter


def test_nav_bar_disables_next_on_last_chapter():
    names = ["ch01_a", "ch02_b", "ch03_c"]
    html = build.nav_bar(names, len(names) - 1)
    assert '<a href="../ch02_b/"' in html  # Previous links to the second chapter
    assert "ml-nav-disabled" in html and "Next &rarr;" in html


def test_nav_bar_links_both_ways_in_middle():
    names = ["ch01_a", "ch02_b", "ch03_c"]
    html = build.nav_bar(names, 1)
    assert '<a href="../ch01_a/"' in html
    assert '<a href="../ch03_c/"' in html
    assert "ml-nav-disabled" not in html


def test_nav_bar_always_links_home():
    names = ["ch01_a"]
    html = build.nav_bar(names, 0)
    assert '<a class="ml-nav-home" href="../">All chapters</a>' in html
