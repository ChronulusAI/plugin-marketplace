#!/usr/bin/env python3
"""Checks that every skill of every plugin meets the marketplace's specs, so a release that claude.ai would sync
with warnings fails here first.

Specs checked, for each `plugins/<plugin>/skills/<skill>/SKILL.md`:
  - it starts with a YAML front matter block that parses to a mapping;
  - the front matter has a non-empty `name` and a non-empty `description`;
  - `description` is at most 1024 characters. claude.ai stores the description cut to 1024 characters (Claude Code
    reads the full text from the file), which drops the end of the text that decides when the skill is used. The
    marketplace shows the sync as "Synced with warnings".

Usage:
    check_plugin_specs.py [plugins_dir]

Prints one line per problem and exits 1 if there are any; prints the length of every description otherwise.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

MAX_DESCRIPTION = 1024
FRONT_MATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.S)


def check_skill(path: Path) -> tuple[list[str], str | None]:
    """Returns the problems of one SKILL.md and a one-line summary of it (None if it could not be read)."""
    problems: list[str] = []
    match = FRONT_MATTER.match(path.read_text(encoding="utf-8"))
    if not match:
        return [f"{path}: no YAML front matter (the file must start with a --- block)"], None
    try:
        front = yaml.safe_load(match.group(1))
    except yaml.YAMLError as e:
        return [f"{path}: the front matter is not valid YAML: {e}"], None
    if not isinstance(front, dict):
        return [f"{path}: the front matter is not a mapping of fields"], None

    name = front.get("name")
    if not isinstance(name, str) or not name.strip():
        problems.append(f"{path}: field 'name' is required")
    description = front.get("description")
    if not isinstance(description, str) or not description.strip():
        problems.append(f"{path}: field 'description' is required and must be text")
        return problems, None
    if len(description) > MAX_DESCRIPTION:
        problems.append(
            f"{path}: field 'description' in SKILL.md must be at most {MAX_DESCRIPTION} characters "
            f"(it has {len(description)}, {len(description) - MAX_DESCRIPTION} too many). claude.ai stores the "
            f"description cut to {MAX_DESCRIPTION} characters, which drops the end of it."
        )
    return problems, f"{path}: description {len(description)}/{MAX_DESCRIPTION} characters"


def main(plugins_dir: str = "plugins") -> int:
    skills = sorted(Path(plugins_dir).glob("*/skills/*/SKILL.md"))
    if not skills:
        print(f"No skills found under {plugins_dir}/*/skills/*/SKILL.md", file=sys.stderr)
        return 1
    problems: list[str] = []
    for path in skills:
        found, summary = check_skill(path)
        problems += found
        if summary and not found:
            print(summary)
    for problem in problems:
        print(f"ERROR {problem}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    if len(sys.argv) > 2:
        sys.exit(__doc__)
    sys.exit(main(*sys.argv[1:]))
