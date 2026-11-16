# Instructions

- Treat [MODEL-SCOPE.md](MODEL-SCOPE.md) as the architectural authority boundary: the metamodel is conceptual, and the validator/workflows are optional project-specific aids.

* Don't be verbose
* prefer bullet lists
* any code should be as simple and compact as possible
* specs must validate with `reference-implementation/metamodel.py` before committing; use `reference-implementation/schema.json` for structured generation; regenerate it (`--schema > schema.json`) when models change
* to run the scripts remotely, dispatch the `metamodel` workflow (`script`: `metamodel.py`|`pytest`, `args`) and read its logs
* when new facts, hidden coupling or model gaps are discovered during work, report feedback to update the spec or metamodel (`CONSTITUTION.md` § Self-Improvement and Model Feedback) rather than working around them silently; issues, PRs and reviews here are public, so follow `README.md` § Giving feedback (no adopting-project names, URLs or content)
* before reporting, re-check the work against the original goal and fix in-scope gaps yourself (stale references, docs a change made inaccurate, gaps found while verifying); report only what needs a decision or permission, or could not be verified, with the reason, and batch approval requests into one question
