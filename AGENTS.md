# Instructions

- Treat [MODEL-SCOPE.md](MODEL-SCOPE.md) as the architectural authority boundary: the metamodel is conceptual, and the validator/workflows are optional project-specific aids.

* Don't be verbose
* prefer bullet lists
* any code should be as simple and compact as possible
* specs must validate with `reference-implementation/metamodel.py` before committing; use `reference-implementation/schema.json` for structured generation; regenerate it (`--schema > schema.json`) when models change
* before pushing, run what CI runs: `uv run pytest -q` (root `tests/`: toolkit manifest, packaging; a new tracked file needs a `toolkit_manifest.txt` entry), `(cd reference-implementation && uv run pytest -q)` and `python3 release_support.py --check-changelog`
* wait for CI by commit, not by "latest run": runs register seconds after a push, so poll `gh run list --commit <sha>` until every workflow has a run and all are completed; after dispatching `publish`, watch the run created after the dispatch, not `gh run list --limit 1` (it may be the previous one)
* to run the scripts remotely, dispatch the `metamodel` workflow (`script`: `metamodel.py`|`pytest`, `args`) and read its logs
* when new facts, hidden coupling or model gaps are discovered during work, report feedback to update the spec or metamodel (`CONSTITUTION.md` § Self-Improvement and Model Feedback) rather than working around them silently; issues, PRs and reviews here are public, so follow `README.md` § Giving feedback (no adopting-project names, URLs or content)
* before reporting, re-check the work against the original goal and fix in-scope gaps yourself (stale references, docs a change made inaccurate, gaps found while verifying); report only what needs a decision or permission, or could not be verified, with the reason, and batch approval requests into one question
