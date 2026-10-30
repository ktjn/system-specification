# Instructions

* Don't be verbose
* prefer bullet lists
* any code should be as simple and compact as possible
* specs must validate with `reference-implementation/metamodel.py` before committing; use `reference-implementation/schema.json` for structured generation; regenerate it (`--schema > schema.json`) when models change
* to run the scripts remotely, dispatch the `metamodel` workflow (`script`: `metamodel.py`|`pytest`, `args`) and read its logs
