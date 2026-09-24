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


def test_zen_profiles_are_one_per_identity() -> None:
    create = (root / "roles/browser/tasks/main.yml").read_text()
    assert "-P Media" in create, "the media profile is seeded here"
    assert "-P GamingMedia" not in create, (
        "a scene's companion browser is a second window of the media profile, "
        "claimed by the scene engine -- no profile exists to carry a window class"
    )


def test_pokemon_profiles_are_named_and_seeded() -> None:
    defaults = (root / "roles/browser/defaults/main.yml").read_text()
    create = (root / "roles/browser/tasks/main.yml").read_text()
    assert "- pokemon-left" in defaults and "- pokemon-right" in defaults
    assert "-P pokemon-left" in create and "-P pokemon-right" in create
    assert "zen_containers" in defaults, "per-profile container identities live in defaults"


def test_shared_zen_prefs_source_exists() -> None:
    user_js = root / "roles/browser/templates/zen-user.js.j2"
    assert user_js.exists()
    assert "prefers-color-scheme" in user_js.read_text() or "accent" in user_js.read_text()


def test_zen_never_restores_the_last_session() -> None:
    user_js = (root / "roles/browser/templates/zen-user.js.j2").read_text()
    assert 'user_pref("browser.startup.page", 1)' in user_js, (
        "startup opens the homepage, not the previous windows"
    )
    assert 'user_pref("browser.sessionstore.resume_from_crash", false)' in user_js, (
        "an unclean exit (shutdown with Zen running) must not replay the session either"
    )
    assert 'user_pref("browser.sessionstore.resume_session_once", false)' in user_js, (
        "a one-off session resume (e.g. after an update) must not replay the session"
    )
    assert 'user_pref("browser.sessionstore.max_resumed_crashes", 0)' in user_js, (
        "even repeated crashes must not offer to replay the session"
    )
