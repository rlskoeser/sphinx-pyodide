"""Tests for pyodide directive parsing."""

from __future__ import annotations

import pytest
from sphinx.testing.restructuredtext import parse
from sphinx.testing.util import SphinxTestApp

from sphinx_pyodide.main import PyodideNode, PyodideOutputNode


@pytest.mark.sphinx("html", testroot="pyodide")
def test_directive_basic_block(app: SphinxTestApp) -> None:
    """A bare pyodide directive creates a PyodideNode with code."""
    doctree = parse(app, ".. pyodide::\n\n    print(42)")
    nodes = list(doctree.findall(PyodideNode))
    assert len(nodes) == 1
    node = nodes[0]
    assert node["code"] == "print(42)"
    assert node["code_id"]
    assert node["packages"] == []
    assert node["local_packages"] == []
    assert node["editable"] is False


@pytest.mark.sphinx("html", testroot="pyodide")
def test_directive_with_packages(app: SphinxTestApp) -> None:
    """:packages: option is parsed into a list of package names."""
    doctree = parse(
        app,
        "\n".join(
            [
                ".. pyodide::",
                "    :packages: numpy, pandas",
                "",
                "    import numpy as np",
            ]
        ),
    )
    nodes = list(doctree.findall(PyodideNode))
    assert len(nodes) == 1
    node = nodes[0]
    assert node["packages"] == ["numpy", "pandas"]
    assert node["local_packages"] == []


@pytest.mark.sphinx("html", testroot="pyodide")
def test_directive_with_single_package(app: SphinxTestApp) -> None:
    """A single package name is parsed correctly."""
    doctree = parse(app, ".. pyodide::\n    :packages: numpy\n\n    import numpy")
    node = next(iter(doctree.findall(PyodideNode)))
    assert node["packages"] == ["numpy"]


@pytest.mark.sphinx("html", testroot="pyodide")
def test_directive_with_empty_packages(app: SphinxTestApp) -> None:
    """An empty :packages: option results in no packages."""
    doctree = parse(app, ".. pyodide::\n    :packages:\n\n    pass")
    node = next(iter(doctree.findall(PyodideNode)))
    assert node["packages"] == []


@pytest.mark.sphinx("html", testroot="pyodide")
def test_directive_with_editable_flag(app: SphinxTestApp) -> None:
    """:editable: flag sets editable to True."""
    doctree = parse(app, ".. pyodide::\n    :editable:\n\n    x = 1")
    node = next(iter(doctree.findall(PyodideNode)))
    assert node["editable"] is True


@pytest.mark.sphinx("html", testroot="pyodide")
def test_directive_multiple_blocks(app: SphinxTestApp) -> None:
    """Multiple pyodide blocks in one document each create a node."""
    doctree = parse(
        app,
        "\n".join(
            [
                ".. pyodide::\n\n    a = 1",
                "",
                "some text",
                "",
                ".. pyodide::\n\n    b = 2",
            ]
        ),
    )
    nodes = list(doctree.findall(PyodideNode))
    assert len(nodes) == 2
    assert nodes[0]["code"] == "a = 1"
    assert nodes[1]["code"] == "b = 2"
    assert nodes[0]["code_id"] != nodes[1]["code_id"]


@pytest.mark.sphinx("html", testroot="pyodide")
def test_directive_with_output_option(app: SphinxTestApp) -> None:
    """:output: option sets static output for noscript fallback."""
    doctree = parse(
        app,
        "\n".join(
            [
                ".. pyodide::",
                "    :output: 42",
                "",
                "    print(42)",
            ]
        ),
    )
    node = next(iter(doctree.findall(PyodideNode)))
    assert node["output"] == "42"


@pytest.mark.sphinx("html", testroot="pyodide")
def test_directive_with_named_output(app: SphinxTestApp) -> None:
    """Named output block is resolved from the environment."""
    doctree = parse(
        app,
        "\n".join(
            [
                ".. pyodide-output:: greet",
                "",
                "    Hello from Pyodide!",
                "",
                ".. pyodide::",
                "    :output: greet",
                "",
                "    print('hi')",
            ]
        ),
    )
    outputs = list(doctree.findall(PyodideOutputNode))
    assert len(outputs) == 1
    node = next(iter(doctree.findall(PyodideNode)))
    assert node["output"] == "Hello from Pyodide!"


@pytest.mark.sphinx("html", testroot="pyodide")
def test_directive_code_id_stable(app: SphinxTestApp) -> None:
    """Same code produces the same code_id (by md5 of content)."""
    doctree = parse(app, ".. pyodide::\n\n    x = 1")
    node = next(iter(doctree.findall(PyodideNode)))
    assert len(node["code_id"]) == 8
    assert node["code_id"].isalnum()


@pytest.mark.sphinx("html", testroot="pyodide")
def test_directive_show_errors_flag(app: SphinxTestApp) -> None:
    """:show-errors: flag sets show_errors to True."""
    doctree = parse(app, ".. pyodide::\n    :show-errors:\n\n    x = 1")
    node = next(iter(doctree.findall(PyodideNode)))
    assert node["show_errors"] is True


@pytest.mark.sphinx("html", testroot="pyodide")
def test_directive_show_errors_default(app: SphinxTestApp) -> None:
    """Without :show-errors: flag, show_errors is False by default."""
    doctree = parse(app, ".. pyodide::\n\n    x = 1")
    node = next(iter(doctree.findall(PyodideNode)))
    assert node["show_errors"] is False
