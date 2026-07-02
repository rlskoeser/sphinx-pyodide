"""Pytest configuration for sphinx-pyodide tests."""

from pathlib import Path

import pytest

pytest_plugins = "sphinx.testing.fixtures"


@pytest.fixture(scope="session")
def rootdir() -> Path:
    """Path to test root directories."""
    return Path(__file__).parent / "roots"
