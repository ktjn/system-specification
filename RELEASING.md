# Releasing

Maintainers only; not shipped in the toolkit.

1. Each PR keeps [`CHANGELOG.md`](CHANGELOG.md) `Unreleased` current (lead with a `Compatibility:` line when relevant).
2. Run **Actions → publish → Run workflow** and pick the bump: new optional field or invariant → `minor`; breaking CLI/export/schema change → `major` (document migration under `Unreleased` first); fixes and docs → `patch`.

The workflow bumps both `pyproject.toml` files, `system_spec_ref/__init__.py` and both lockfiles, turns `Unreleased` into the version heading, runs tests, builds, pushes commit `Release X.Y.Z` and tag `vX.Y.Z` to `main`, publishes to PyPI through trusted publishing (`pypi` environment) and creates the GitHub release with the distributions, notes and SHA-256 digests (the release record). It needs `github-actions[bot]` allowed to push to `main`. A PyPI version cannot be reused; if PyPI fails after the push, re-run the failed jobs.
