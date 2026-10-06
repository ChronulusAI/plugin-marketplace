#!/usr/bin/env python3
"""Bumps the patch version in plugin.json for every plugin changed between two commits.

A plugin counts as changed when any file under plugins/<name>/ changed, other than that
plugin's own .claude-plugin/plugin.json (so a bump commit never triggers another bump).

Usage:
    bump_plugin_versions.py <base_sha> <head_sha>

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
SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
ZERO_SHA = "0" * 40


def changed_files(base: str, head: str) -> list[str]:
    if base == ZERO_SHA:
        base = f"{head}~1"
    out = subprocess.run(
        ["git", "diff", "--name-only", base, head],
        check=True, capture_output=True, text=True,
    ).stdout
    return [line for line in out.splitlines() if line]


def changed_plugins(files: list[str]) -> list[str]:
    names = set()
    for f in files:
        parts = f.split("/")
        if len(parts) < 3 or parts[0] != PLUGINS_DIR:
            continue
        if "/".join(parts[2:]) == MANIFEST:
            continue
        names.add(parts[1])
    return sorted(names)


def bump_patch(version: str) -> str:
    m = SEMVER.match(version)
    if not m:
        raise ValueError(f"version {version!r} is not MAJOR.MINOR.PATCH")
    major, minor, patch = map(int, m.groups())
    return f"{major}.{minor}.{patch + 1}"


def main(base: str, head: str) -> None:
    for name in changed_plugins(changed_files(base, head)):
        path = Path(PLUGINS_DIR) / name / MANIFEST
        if not path.exists():
            continue  # a directory under plugins/ that isn't a plugin (or was deleted)
        text = path.read_text()
        data = json.loads(text)
        old = data["version"]
        new = bump_patch(old)
        # Rewrite just the version string so the rest of the file's formatting is untouched.
        path.write_text(re.sub(r'("version"\s*:\s*")[^"]*(")', rf"\g<1>{new}\g<2>", text, count=1))
        print(f"{name} {old} -> {new}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
