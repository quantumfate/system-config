"""Baseline regression tests for this repo's own rendered curriculum.

The repo had no test suite until now — `just check` collected nothing
(pytest exits 5 on zero tests, which fails `just check`). These pin the
delivered pieces this session changed, so a rename here has to travel with the
in-template contract.
"""

from pathlib import Path

root = Path(__file__).resolve().parent.parent


def test_the_store_directory_is_knob_surface() -> None:
    env = (root / "roles/theming/templates/environment.d-theming.conf.j2").read_text()
    assert "QF_STORE" in env, "user units need the shared quantum-store directory"


def test_gaming_media_profile_is_first_class() -> None:
    create = (root / "roles/browser_profiles/tasks/main.yml").read_text()
    assert "-P GamingMedia" in create, (
        "the gaming scene's companion rides its own zen profile; the seed list names it"
    )


def test_shared_zen_prefs_source_exists() -> None:
    user_js = root / "roles/theming/templates/zen-user.js.j2"
    assert user_js.exists()
    assert "prefers-color-scheme" in user_js.read_text() or "accent" in user_js.read_text()
