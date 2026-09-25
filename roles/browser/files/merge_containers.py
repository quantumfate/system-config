#!/usr/bin/env python3
"""Merge role-declared container identities into one Zen profile's containers.json.

The role provisions container *identities* per profile (the flat v6 file Zen
reads), never the default-container choice — that is a Zen UI decision made
after provisioning and stored outside this file. The merge is keyed by name:
an identity already present keeps its userContextId and its own icon/color, so
site associations, user-picked ids and cosmetic tweaks survive a re-converge;
an identity that is missing is appended with a fresh id and the declared seed
icon/color. `siteAssociations` and the two internal identities are preserved
wholesale. The file is written only when something actually changed, so a
converge that declares nothing new leaves an untouched mtime.

Usage: merge_containers.py CONFIG_ROOT PROFILE_DIR DECLARED_JSON
  CONFIG_ROOT     the profile parent (a `.config/zen`), for profiles.ini
  PROFILE_DIR     the profile directory whose containers.json to merge into
  DECLARED_JSON   rendered `zen_containers` map: profile name -> [identity]
"""

import configparser
import json
import sys
from pathlib import Path

VERSION = 6
INTERNAL_THUMBNAIL = 5
INTERNAL_WEBEXT = 4294967295
INTERNAL_NAMES = {
    INTERNAL_THUMBNAIL: "userContextIdInternal.thumbnail",
    INTERNAL_WEBEXT: "userContextIdInternal.webextStorageLocal",
}


def profile_name(config_root: Path, profile_dir: Path) -> str:
    """Resolve profiles.ini's Name for a profile directory path."""
    ini = config_root / "profiles.ini"
    if ini.exists():
        parser = configparser.ConfigParser()
        parser.optionxform = str  # keep profiles.ini's Name= / Path= casing
        parser.read(ini)
        for section in parser.sections():
            if section.startswith("Profile"):
                path = parser.get(section, "Path", fallback="")
                if Path(path).name == profile_dir.name:
                    return parser.get(section, "Name", fallback=profile_dir.name)
    # A just-created profile (or a missing profiles.ini) falls back to the
    # directory suffix after the install salt.
    return profile_dir.name.split(".", 1)[1]


def load_existing(path: Path) -> dict:
    if path.exists():
        data = json.loads(path.read_text())
        if data.get("version") != VERSION:
            # Rendered by a newer Zen; merge onto what it wrote, keep version.
            data.setdefault("version", VERSION)
        return data
    return {
        "version": VERSION,
        "lastUserContextId": INTERNAL_THUMBNAIL,
        "identities": [
            {
                "public": False,
                "icon": "",
                "color": "",
                "name": INTERNAL_NAMES[INTERNAL_THUMBNAIL],
                "accessKey": "",
                "userContextId": INTERNAL_THUMBNAIL,
            },
            {
                "public": False,
                "icon": "",
                "color": "",
                "name": INTERNAL_NAMES[INTERNAL_WEBEXT],
                "accessKey": "",
                "userContextId": INTERNAL_WEBEXT,
            },
        ],
        "siteAssociations": {},
    }


def next_id(identities: list[dict]) -> int:
    used = {
        int(i["userContextId"])
        for i in identities
        if str(i.get("userContextId", "")).isdigit()
        and int(i["userContextId"]) not in INTERNAL_NAMES
    }
    candidate = max(used, default=INTERNAL_THUMBNAIL) + 1
    while candidate in INTERNAL_NAMES:
        candidate += 1
    return candidate


def merge(profile_dir: Path, declared: list[dict]) -> bool:
    path = profile_dir / "containers.json"
    data = load_existing(path)
    identities = data.setdefault("identities", [])
    declared_ids = set()

    for identity in identities:
        name = identity.get("name", "")
        if name in INTERNAL_NAMES.values():
            continue
        declared_ids.add(name)

    changed = False
    for desired in declared:
        name = desired.get("name")
        if not name or name in declared_ids:
            continue
        identity = {
            "userContextId": next_id(identities),
            "public": True,
            "icon": desired.get("icon", "circle"),
            "color": desired.get("color", "blue"),
            "name": name,
        }
        identities.append(identity)
        declared_ids.add(name)
        changed = True

    if changed:
        data["lastUserContextId"] = max(
            int(i["userContextId"])
            for i in identities
            if int(i["userContextId"]) not in INTERNAL_NAMES
        )
        rendered = json.dumps(data, indent=2) + "\n"
        if path.exists() and path.read_text() == rendered:
            return False
        path.write_text(rendered)
    return changed


def main() -> int:
    if len(sys.argv) != 4:
        print(__doc__, file=sys.stderr)
        return 2
    config_root = Path(sys.argv[1])
    profile_dir = Path(sys.argv[2])
    declared = json.loads(Path(sys.argv[3]).read_text())
    name = profile_name(config_root, profile_dir)
    wanted = declared.get(name) or []
    if not wanted or not profile_dir.is_dir():
        return 0
    if merge(profile_dir, wanted):
        print(f"containers updated: {name} -> {len(wanted)} identities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
