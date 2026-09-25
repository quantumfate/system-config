"""Search engine configuration: DuckDuckGo default, one-offs hidden in mozlz4.

Modern Firefox / Zen ignore `browser.search.defaultenginename` in `user.js` and
store the active search engine configuration in `search.json.mozlz4`. These pin
the contract of `roles/browser/files/configure_search.py`.
"""

import subprocess
from pathlib import Path
import pytest

root = Path(__file__).resolve().parent.parent
script = root / "roles/browser/files/configure_search.py"

# Import helper functions directly from configure_search
import sys

sys.path.insert(0, str(script.parent))
from configure_search import compress, decompress, get_lz4, HIDDEN_ENGINES


FIXTURE_DATA = {
    "version": 14,
    "metaData": {
        "appDefaultEngineId": "google",
        "current": "google",
        "defaultEngineId": "google",
    },
    "engines": [
        {"_name": "Google", "id": "google", "_metaData": {}},
        {"_name": "Bing", "id": "bing", "_metaData": {}},
        {"_name": "DuckDuckGo", "id": "ddg", "_metaData": {}},
        {"_name": "Ecosia", "id": "ecosia", "_metaData": {}},
        {"_name": "Perplexity", "id": "perplexity", "_metaData": {}},
        {"_name": "Startpage", "id": "startpage", "_metaData": {}},
        {"_name": "Wikipedia (en)", "id": "wikipedia", "_metaData": {}},
    ],
}


def test_configures_duckduckgo_and_hides_one_offs(tmp_path: Path) -> None:
    lz4 = get_lz4()
    if not lz4:
        pytest.skip("liblz4 not available")

    profile = tmp_path / "vzn4dz01.Default (twilight)"
    profile.mkdir()
    search_file = profile / "search.json.mozlz4"
    search_file.write_bytes(compress(lz4, FIXTURE_DATA))

    res = subprocess.run(["python3", str(script), str(profile)], capture_output=True, text=True)
    assert res.returncode == 0
    assert "search configured" in res.stdout

    updated = decompress(lz4, search_file.read_bytes())
    assert updated["metaData"]["appDefaultEngineId"] == "ddg"
    assert updated["metaData"]["defaultEngineId"] == "ddg"
    assert updated["metaData"]["current"] == "ddg"

    for engine in updated["engines"]:
        name = engine["_name"]
        if name == "DuckDuckGo":
            assert engine["_metaData"]["hideOneOffButton"] is False
        elif name in HIDDEN_ENGINES:
            assert engine["_metaData"]["hideOneOffButton"] is True

    # Idempotent re-run
    res2 = subprocess.run(["python3", str(script), str(profile)], capture_output=True, text=True)
    assert res2.returncode == 0
    assert "search configured" not in res2.stdout
