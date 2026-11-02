# Reference Implementation

Validates [spec.md](../spec.md) with Python, Pydantic, YAML, and pytest.

- Validate spec: `uv run python metamodel.py example.yaml`
- Export schema: `uv run python metamodel.py --schema`
- Impact analysis: `uv run python metamodel.py example.yaml --impact order`
- Compatibility: `uv run python metamodel.py new.yaml --compat old.yaml`
- JSON output: add `--json`
- Self-check (every test traces to a requirement): `uv run pytest --junitxml=report.xml && uv run python metamodel.py metamodel.yaml --junit report.xml`
- Tests must carry `@pytest.mark.verifies("<requirement>@<version>")`; `conftest.py` aborts collection otherwise
- Run tests: `uv run pytest`
- Docker: `docker build -t metamodel . && docker run --rm metamodel [python metamodel.py ... | pytest]`
- Remote: `.github/workflows/metamodel.yml` runs either script in Docker when dispatched manually (`script`, `args`)
