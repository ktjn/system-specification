# Instructions

* Don't be verbose
* prefer bullet lists
* any code should be as simple and compact as possible
* specs must validate with `reference-implementation/metamodel.py` before committing; use `reference-implementation/schema.json` for structured generation; regenerate it (`--schema > schema.json`) when models change
* to run the scripts remotely, dispatch the `metamodel` workflow (`script`: `metamodel.py`|`pytest`, `args`) and read its logs
* when new facts, hidden coupling or model gaps are discovered during work, report feedback to update the spec or metamodel (`CONSTITUTION.md` § Self-Improvement and Model Feedback) rather than working around them silently
