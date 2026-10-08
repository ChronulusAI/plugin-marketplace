#!/usr/bin/env python3
"""Bumps the patch version of every plugin changed on this branch relative to a base ref.

A plugin counts as changed when any file under plugins/<name>/ differs from the base
(merge-base diff), other than that plugin's own manifests. The Claude manifest
(.claude-plugin/plugin.json) is the source of truth for the version; the Codex manifest
(plugin.json) is kept in sync with it.

The bump is relative to the version on the base ref, and only happens when this branch's
version is not already ahead of it. That makes the script idempotent (one bump per release
candidate, however many pushes) and lets a release candidate that falls behind a newer
release re-bump past it.

Usage:
    bump_plugin_versions.py <base_ref>

Prints one "<plugin> <old> -> <new>" line per bumped plugin, and nothing if none changed.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

PLUGINS_DIR = "plugins"
MANIFEST = ".claude-plugin/plugin.json"
CODEX_MANIFEST = "plugin.json"
SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def changed_files(base: str) -> list[str]:
    out = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...HEAD"],
        check=True, capture_output=True, text=True,
    ).stdout
    return [line for line in out.splitlines() if line]


def changed_plugins(files: list[str]) -> list[str]:
    names = set()
    for f in files:
        parts = f.split("/")
        if len(parts) < 3 or parts[0] != PLUGINS_DIR:
            continue
        if "/".join(parts[2:]) in (MANIFEST, CODEX_MANIFEST):
            continue
        names.add(parts[1])
    return sorted(names)


def bump_patch(version: str) -> str:
    m = SEMVER.match(version)
    if not m:
        raise ValueError(f"version {version!r} is not MAJOR.MINOR.PATCH")
    major, minor, patch = map(int, m.groups())
    return f"{major}.{minor}.{patch + 1}"


def parse(version: str) -> tuple[int, int, int]:
    m = SEMVER.match(version)
    if not m:
        raise ValueError(f"version {version!r} is not MAJOR.MINOR.PATCH")
    return tuple(map(int, m.groups()))


def base_version(base: str, path: Path) -> str | None:
    """The plugin's version on the base ref, or None if the plugin is new there."""
    res = subprocess.run(
        ["git", "show", f"{base}:{path.as_posix()}"], capture_output=True, text=True,
    )
    return json.loads(res.stdout)["version"] if res.returncode == 0 else None


def main(base: str) -> None:
    for name in changed_plugins(changed_files(base)):
        path = Path(PLUGINS_DIR) / name / MANIFEST
        if not path.exists():
            continue  # a directory under plugins/ that isn't a plugin (or was deleted)
        released = base_version(base, path)
        if released is None:
            continue  # a new plugin: it ships at whatever version it declares
        current = json.loads(path.read_text())["version"]
        if parse(current) > parse(released):
            continue  # already bumped for this release
        new = bump_patch(released)
        # Rewrite just the version string so the rest of the file's formatting is untouched.
        for manifest in (path, path.parent.parent / CODEX_MANIFEST):
            if manifest.exists():
                text = manifest.read_text()
                manifest.write_text(re.sub(r'("version"\s*:\s*")[^"]*(")', rf"\g<1>{new}\g<2>", text, count=1))
        print(f"{name} {current} -> {new}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
