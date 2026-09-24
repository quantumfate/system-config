#!/usr/bin/env python3
"""Configure DuckDuckGo default engine and hide one-offs in search.json.mozlz4.

Modern Firefox and Zen store the active default search engine and the
per-engine one-off button visibility in `search.json.mozlz4`, ignoring legacy
`browser.search.defaultenginename` preferences in `user.js` once the search
store exists. This script patches the profile's `search.json.mozlz4` using liblz4
to enforce DuckDuckGo as default and hide the specified one-off engines.
"""

import ctypes
import ctypes.util
import json
import struct
import sys
from pathlib import Path

MAGIC = b"mozLz40\0"
HIDDEN_ENGINES = {
    "Bing",
    "Ecosia",
    "Google",
    "Perplexity",
    "Startpage",
    "Wikipedia (en)",
}


def get_lz4():
    libname = ctypes.util.find_library("lz4")
    if not libname:
        return None
    return ctypes.CDLL(libname)


def decompress(lz4, raw: bytes) -> dict:
    if not raw.startswith(MAGIC) or len(raw) < 12:
        return {}
    uncompressed_size = struct.unpack("<I", raw[8:12])[0]
    out_buf = ctypes.create_string_buffer(uncompressed_size)
    res = lz4.LZ4_decompress_safe(raw[12:], out_buf, len(raw) - 12, uncompressed_size)
    if res <= 0:
        return {}
    return json.loads(out_buf.raw[:res].decode("utf-8"))


def compress(lz4, data: dict) -> bytes:
    raw_json = json.dumps(data, separators=(",", ":")).encode("utf-8")
    uncompressed_size = len(raw_json)
    max_comp_size = uncompressed_size * 2 + 64
    out_buf = ctypes.create_string_buffer(max_comp_size)
    comp_size = lz4.LZ4_compress_default(
        raw_json, out_buf, uncompressed_size, max_comp_size
    )
    header = MAGIC + struct.pack("<I", uncompressed_size)
    return header + out_buf.raw[:comp_size]


def configure(profile_dir: Path) -> bool:
    search_file = profile_dir / "search.json.mozlz4"
    if not search_file.exists():
        return False
    lz4 = get_lz4()
    if not lz4:
        return False

    try:
        data = decompress(lz4, search_file.read_bytes())
    except Exception:
        return False
    if not data:
        return False

    changed = False
    meta = data.setdefault("metaData", {})
    if meta.get("appDefaultEngineId") != "ddg":
        meta["appDefaultEngineId"] = "ddg"
        changed = True
    if meta.get("defaultEngineId") != "ddg":
        meta["defaultEngineId"] = "ddg"
        changed = True
    if meta.get("current") != "ddg":
        meta["current"] = "ddg"
        changed = True

    for engine in data.get("engines", []):
        name = engine.get("_name") or engine.get("name") or ""
        eid = engine.get("id", "")
        is_ddg = eid == "ddg" or name == "DuckDuckGo"
        engine_meta = engine.setdefault("_metaData", {})
        if is_ddg:
            if engine_meta.get("hideOneOffButton") is not False:
                engine_meta["hideOneOffButton"] = False
                changed = True
        elif name in HIDDEN_ENGINES or eid.lower() in {h.lower() for h in HIDDEN_ENGINES}:
            if engine_meta.get("hideOneOffButton") is not True:
                engine_meta["hideOneOffButton"] = True
                changed = True

    if changed:
        search_file.write_bytes(compress(lz4, data))
        return True
    return False


def main() -> int:
    if len(sys.argv) < 2:
        return 2
    for arg in sys.argv[1:]:
        p = Path(arg)
        if configure(p):
            print(f"search configured: {p.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
