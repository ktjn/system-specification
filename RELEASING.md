# Releasing

Maintainers only; not shipped in the toolkit.

## Setup (once)

- Allow `github-actions[bot]` to push to `main` (the workflow pushes the release commit and tag).
- PyPI trusted publisher: project `system-spec-ref`, workflow `publish.yml`, environment `pypi`.

## Every PR

- Keep [`CHANGELOG.md`](CHANGELOG.md) `Unreleased` current; lead with a `Compatibility:` line when relevant.

## Release

1. Check `Unreleased` lists everything since the last tag and is not empty.
2. Pick the bump; with mixed changes take the highest:
   - `major`: breaking CLI, export or schema change (write the migration under `Unreleased` first);
   - `minor`: new optional field, option or invariant;
   - `patch`: fixes and docs only.
3. Run **Actions → publish → Run workflow** on `main` with that bump.
4. Verify: the new version is on PyPI, and GitHub release `vX.Y.Z` has the distributions, notes and SHA-256 digests (the release record).

The workflow bumps both `pyproject.toml` files, `system_spec_ref/__init__.py` and both lockfiles, turns `Unreleased` into the version heading, runs tests, builds, pushes commit `Release X.Y.Z` and tag `vX.Y.Z` to `main`, publishes to PyPI (trusted publishing) and creates the GitHub release.

## If it fails

- A PyPI version cannot be reused.
- Before the push step: nothing was released; fix and run again.
- After the push (tag exists): re-run only the failed jobs. Never re-run the whole workflow; it would bump the version again.
