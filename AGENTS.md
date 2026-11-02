# Instructions

* Don't be verbose
* prefer bullet lists
* any code should be as simple and compact as possible
* every test must carry `@pytest.mark.verifies("<req>@<ver>")`; run `self-check` before committing
* specs must validate with `reference-implementation/metamodel.py` before committing; use `--schema` for structured generation
* to run the scripts remotely, dispatch the `metamodel` workflow (`script`: `metamodel.py`|`pytest`|`self-check`, `args`) and read its logs
