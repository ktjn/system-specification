import pytest

def pytest_configure(config):
    config.addinivalue_line("markers", "verifies(ref): requirement 'id@version' the test verifies")

def pytest_collection_modifyitems(items):
    bad = [i.nodeid for i in items if len(list(i.iter_markers("verifies"))) != 1]
    if bad: pytest.exit(f"tests must carry exactly one verifies marker: {bad}", returncode=4)
    for i in items: i.user_properties.append(("verifies", i.get_closest_marker("verifies").args[0]))
