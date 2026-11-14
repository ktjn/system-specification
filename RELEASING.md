# Releasing

Maintainers only; not shipped in the toolkit.

## Setup (once)

- Allow `github-actions[bot]` to push to `main` (the workflow pushes the release commit and tag).
- PyPI trusted publisher: project `system-spec-ref`, workflow `publish.yml`, environment `pypi`.

## Release

Run **Actions → publish → Run workflow** on `main`. Nothing else is needed.

- It suggests the version as the higher of two signals:
  - the public surface since the last tag: `major` if an invariant ID, CLI option or schema property was removed, `minor` if one was added;
  - the change types declared in [`CHANGELOG.md`](CHANGELOG.md) `Unreleased`: `Breaking:` is `major`, `Added:` is `minor`, `Changed:` and `Fixed:` are `patch`.
- It stops if `Unreleased` is empty or an entry has no change-type prefix.
- `dry_run` only shows the plan: version, reasons and entries. Read it in the job log (step "plan"), the run's annotations and its Summary tab.
- `bump` overrides the suggestion, e.g. `major` for a breaking behaviour change that no removed item shows (write the migration under `Unreleased` first).
- It then bumps both `pyproject.toml` files, `system_spec_ref/__init__.py` and both lockfiles, turns `Unreleased` into the version heading, runs tests, builds, pushes commit `Release X.Y.Z` and tag `vX.Y.Z` to `main`, publishes to PyPI and creates the GitHub release (distributions, notes, SHA-256 digests: the release record).

## Every PR

- Add a `CHANGELOG.md` `Unreleased` entry starting with `Breaking:`, `Added:`, `Changed:` or `Fixed:` (mention compatibility in the text); CI fails a PR that changes `metamodel.py` or a schema without an entry, or whose entries lack the prefix.

## If it fails

- A PyPI version cannot be reused.
- Re-running the whole workflow is safe: if `HEAD` already carries a version tag, it resumes that release (no second bump) and skips what already exists on PyPI and GitHub.
- If more commits reached `main` after the failed push, re-running starts a new release instead; resume first by re-running the failed jobs of the original run.
