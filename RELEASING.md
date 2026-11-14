# Releasing

Maintainers only; not shipped in the toolkit.

1. Update [`CHANGELOG.md`](CHANGELOG.md): move `Unreleased` items under the new version.
2. Bump the version in `pyproject.toml`, `reference-implementation/pyproject.toml` and `system_spec_ref/__init__.py`; run `uv lock` in the root and in `reference-implementation/`. A test keeps the two `pyproject.toml` versions equal.
3. Version number: new optional field or invariant → minor; breaking CLI/export/schema change → major (document migration); fixes and docs → patch.
4. Open a PR; `package` CI must pass (build, tests, installed-wheel smoke on Ubuntu with the latest Python; `PKG-09`).
5. After merge, publish a GitHub release `vX.Y.Z` on `main`. `publish.yml` runs tests, builds and publishes to PyPI through trusted publishing (`pypi` environment); it fails unless the tag equals the `pyproject.toml` version. A PyPI version cannot be reused.
6. Record the tag commit and published SHA-256 digests in the release record in [`PACKAGING.md`](PACKAGING.md).
