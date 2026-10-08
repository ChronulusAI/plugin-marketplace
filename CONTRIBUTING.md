# Contributing

## Adding a plugin

To add a new plugin:

1. Create `plugins/<plugin-name>/` with a `.claude-plugin/plugin.json` manifest (and a
   `plugin.json` for Codex) and whatever components it needs (`skills/`, `commands/`,
   `agents/`, `hooks/`, `.mcp.json` / `mcp.json`).
2. Add an entry for it to the `plugins` array in both `.claude-plugin/marketplace.json`
   and `.agents/plugins/marketplace.json`.
3. Give it its own `README.md` documenting what it does and any prerequisites.

## Releasing

`main` only accepts pull requests from `rc/<name>` release-candidate branches, so a
version bump can land before the squash merge:

1. Create `rc/<name>` from `main` (for example `rc/error-guidance`). Use a new name for
   each release; don't reuse branches.
2. Open feature PRs against that `rc/` branch. Test the candidate by installing from it,
   e.g. `codex plugin marketplace add ChronulusAI/plugin-marketplace --ref rc/<name>`.
3. The Release Candidate workflow bumps the patch version of each changed plugin in both
   manifests, once per release, on the `rc/` branch.
4. Merge `main` into the `rc/` branch if `main` has moved, then open a PR from `rc/<name>`
   to `main` and squash-merge it. A PR into `main` from any other branch fails the
   workflow's guard check.
