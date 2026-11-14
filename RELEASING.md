# Releasing

Maintainers only; not shipped in the toolkit.

## Setup (once)

- Allow `github-actions[bot]` to push to `main` (the workflow pushes the release commit and tag).
- PyPI trusted publisher: project `system-spec-ref`, workflow `publish.yml`, environment `pypi`.

## Release

Run **Actions → publish → Run workflow** on `main`. Nothing else is needed.

- It suggests the version: `major` if a public item was removed since the last tag, `minor` if one was added, else `patch`. Public items are invariant IDs, CLI options and schema properties.
- It stops if `Unreleased` in [`CHANGELOG.md`](CHANGELOG.md) is empty.
- `dry_run` only shows the version, the reasons and the `Unreleased` entries (job summary).
- `bump` overrides the suggestion, e.g. `major` for a breaking behaviour change that no removed item shows (write the migration under `Unreleased` first).
- It then bumps both `pyproject.toml` files, `system_spec_ref/__init__.py` and both lockfiles, turns `Unreleased` into the version heading, runs tests, builds, pushes commit `Release X.Y.Z` and tag `vX.Y.Z` to `main`, publishes to PyPI and creates the GitHub release (distributions, notes, SHA-256 digests: the release record).

## Every PR

- CI fails a PR that changes `metamodel.py` or a schema without a `CHANGELOG.md` entry; lead with a `Compatibility:` line when relevant.

## If it fails

- A PyPI version cannot be reused.
- Re-running the whole workflow is safe: if `HEAD` already carries a version tag, it resumes that release (no second bump) and skips what already exists on PyPI and GitHub.
- If more commits reached `main` after the failed push, re-running starts a new release instead; resume first by re-running the failed jobs of the original run.
