"""Container identity merge: declared identities land per profile, merge by name.

The role provisions container *identities* (v6 flat JSON) into each Zen
profile and never writes the default-container choice — that stays a Zen UI
decision. These pin the contract of `roles/browser/files/merge_containers.py`:
existing identities keep their userContextId/icon/color, missing ones are
appended with fresh ids, and a no-op run leaves the file byte-identical.
"""

import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
script = root / "roles/browser/files/merge_containers.py"

MAIN = {
    "version": 6,
    "lastUserContextId": 13,
    "identities": [
        {"public": False, "icon": "", "color": "", "name": "userContextIdInternal.thumbnail", "accessKey": "", "userContextId": 5},
        {"userContextId": 4294967295, "public": False, "icon": "", "color": "", "name": "userContextIdInternal.webextStorageLocal", "accessKey": ""},
        {"userContextId": 10, "public": True, "icon": "fingerprint", "color": "blue", "name": "Personal"},
        {"userContextId": 11, "public": True, "icon": "tree", "color": "pink", "name": "Studying"},
        {"userContextId": 12, "public": True, "icon": "circle", "color": "blue", "name": "Productivity"},
        {"userContextId": 13, "public": True, "icon": "circle", "color": "green", "name": "Sensitive Research"},
    ],
    "siteAssociations": {},
}

DECLARED = {
    "Default (twilight)": [
        {"name": "Personal", "icon": "fingerprint", "color": "blue"},
        {"name": "Studying", "icon": "tree", "color": "pink"},
        {"name": "Productivity", "icon": "circle", "color": "blue"},
        {"name": "Research", "icon": "circle", "color": "turquoise"},
        {"name": "Sensitive Research", "icon": "circle", "color": "green"},
    ]
}


def _run(config_root: Path, profile_dir: Path, declared: dict) -> subprocess.CompletedProcess:
    declared_json = config_root / "declared.json"
    declared_json.write_text(json.dumps(declared))
    return subprocess.run(
        ["python3", str(script), str(config_root), str(profile_dir), str(declared_json)],
        capture_output=True,
        text=True,
    )


def test_adds_missing_identity_by_next_id(tmp_path: Path) -> None:
    config = tmp_path / "zen"
    (config / "vzn4dz01.Default (twilight)").mkdir(parents=True)
    profile = config / "vzn4dz01.Default (twilight)"
    (profile / "containers.json").write_text(json.dumps(MAIN))
    (config / "profiles.ini").write_text(
        "[General]\nVersion=2\n[Profile2]\nName=Default (twilight)\n"
        "IsRelative=1\nPath=vzn4dz01.Default (twilight)\nDefault=1\n"
    )

    result = _run(config, profile, DECLARED)
    assert result.returncode == 0
    data = json.loads((profile / "containers.json").read_text())
    names = {(i["name"], i["userContextId"], i["icon"], i["color"]) for i in data["identities"]}
    assert ("Research", 14, "circle", "turquoise") in names
    assert ("Sensitive Research", 13, "circle", "green") in names
    assert ("Personal", 10, "fingerprint", "blue") in names
    assert data["lastUserContextId"] == 14


def test_existing_identities_keep_their_ids(tmp_path: Path) -> None:
    config = tmp_path / "zen"
    (config / "vzn4dz01.Dofus").mkdir(parents=True)
    profile = config / "vzn4dz01.Dofus"
    existing = {
        "version": 6,
        "lastUserContextId": 6,
        "identities": [
            {"public": False, "icon": "", "color": "", "name": "userContextIdInternal.thumbnail", "accessKey": "", "userContextId": 5},
            {"userContextId": 4294967295, "public": False, "icon": "", "color": "", "name": "userContextIdInternal.webextStorageLocal", "accessKey": ""},
            {"userContextId": 6, "public": True, "icon": "circle", "color": "blue", "name": "Dofus"},
        ],
        "siteAssociations": {"dofus.example.com": 6},
    }
    (profile / "containers.json").write_text(json.dumps(existing))
    (config / "profiles.ini").write_text(
        "[Profile0]\nName=Dofus\nIsRelative=1\nPath=vzn4dz01.Dofus\n"
    )

    result = _run(config, profile, {"Dofus": [{"name": "Dofus", "icon": "circle", "color": "pink"}]})
    assert result.returncode == 0
    data = json.loads((profile / "containers.json").read_text())
    dofus = next(i for i in data["identities"] if i["name"] == "Dofus")
    assert dofus["userContextId"] == 6, "the existing id must survive a re-converge"
    assert dofus["color"] == "blue", "the user's icon/color wins over the seed"
    assert data["siteAssociations"] == {"dofus.example.com": 6}


def test_noop_run_is_byte_idempotent(tmp_path: Path) -> None:
    config = tmp_path / "zen"
    (config / "vzn4dz01.Default (twilight)").mkdir(parents=True)
    profile = config / "vzn4dz01.Default (twilight)"
    (profile / "containers.json").write_text(json.dumps(MAIN))
    (config / "profiles.ini").write_text(
        "[Profile2]\nName=Default (twilight)\nIsRelative=1\n"
        "Path=vzn4dz01.Default (twilight)\nDefault=1\n"
    )
    # First run brings the profile in line; a second run must not rewrite it.
    _run(config, profile, DECLARED)
    after_first = (profile / "containers.json").read_text()
    _run(config, profile, DECLARED)
    assert (profile / "containers.json").read_text() == after_first


def test_undeclared_profile_is_left_alone(tmp_path: Path) -> None:
    config = tmp_path / "zen"
    (config / "vzn4dz01.Media").mkdir(parents=True)
    profile = config / "vzn4dz01.Media"
    containers = {"version": 6, "lastUserContextId": 10, "identities": [], "siteAssociations": {}}
    (profile / "containers.json").write_text(json.dumps(containers))
    (config / "profiles.ini").write_text(
        "[Profile0]\nName=Media\nIsRelative=1\nPath=vzn4dz01.Media\n"
    )

    result = _run(config, profile, {"Dofus": [{"name": "Dofus"}]})
    assert result.returncode == 0
    assert json.loads((profile / "containers.json").read_text()) == containers


def test_profile_name_known_via_profiles_ini(tmp_path: Path) -> None:
    config = tmp_path / "zen"
    # Profile dir whose directory suffix would *not* match the declared name;
    # profiles.ini carries the real Name.
    (config / "vzn4dz01.customsalt").mkdir(parents=True)
    profile = config / "vzn4dz01.customsalt"
    (profile / "containers.json").write_text(json.dumps(MAIN))
    (config / "profiles.ini").write_text(
        "[Profile1]\nName=Default (twilight)\nIsRelative=1\n"
        "Path=vzn4dz01.customsalt\nDefault=1\n"
    )

    result = _run(config, profile, DECLARED)
    assert result.returncode == 0
    names = [i["name"] for i in json.loads((profile / "containers.json").read_text())["identities"]]
    assert "Research" in names, "the declared name maps through profiles.ini, not the dir suffix"