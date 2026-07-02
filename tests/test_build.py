"""Tests for the HTML build output of pyodide directives."""

from __future__ import annotations

import re
from html.parser import HTMLParser
from io import StringIO

import pytest
from sphinx.testing.util import SphinxTestApp


class _PyodideBlockParser(HTMLParser):
    """Extract pyodide block info from built HTML."""

    def __init__(self) -> None:
        super().__init__()
        self.blocks: list[dict[str, str | list[str]]] = []
        self._current_block: dict[str, str | list[str]] | None = None
        self._in_code: bool = False
        self._in_output: bool = False
        self._capturing: bool = False
        self._captured: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        cls = attrs_dict.get("class", "")
        if "pyodide-block" in cls:
            self._current_block = {"id": attrs_dict.get("id", "")}
            self.blocks.append(self._current_block)
        if "pyodide-code" in cls and tag == "pre":
            self._in_code = True
            if self._current_block is not None:
                self._current_block["code"] = ""
        if "pyodide-output" in cls and tag == "pre":
            self._in_output = True
        if tag == "script" and cls == "deps":
            self._capturing = True
            self._captured = []

    def handle_endtag(self, tag: str) -> None:
        if self._in_code and tag == "pre":
            self._in_code = False
        if self._in_output and tag == "pre":
            self._in_output = False
        if self._capturing and tag == "script":
            self._capturing = False
            if self._current_block is not None:
                self._current_block["deps"] = "".join(self._captured)
            self._captured = []

    def handle_data(self, data: str) -> None:
        if self._in_code and self._current_block is not None:
            current = self._current_block["code"]
            if isinstance(current, str):
                self._current_block["code"] = current + data
        if self._capturing:
            self._captured.append(data)


@pytest.mark.sphinx("html", testroot="pyodide")
def test_build_succeeds(app: SphinxTestApp, warning: StringIO) -> None:
    """Sphinx build completes without warnings."""
    app.build()
    assert "failed" not in warning.getvalue().lower()


@pytest.mark.sphinx("html", testroot="pyodide")
def test_build_produces_output_files(app: SphinxTestApp) -> None:
    """Build produces an HTML file and copies static assets."""
    app.build()
    index_html = app.outdir / "index.html"
    assert index_html.exists()

    static_js = app.outdir / "_static" / "sphinx_pyodide.js"
    assert static_js.exists()

    static_css = app.outdir / "_static" / "sphinx_pyodide.css"
    assert static_css.exists()


@pytest.mark.sphinx("html", testroot="pyodide")
def test_pyodide_blocks_rendered(app: SphinxTestApp) -> None:
    """HTML output contains expected pyodide-block elements."""
    app.build()
    html = (app.outdir / "index.html").read_text(encoding="utf-8")

    parser = _PyodideBlockParser()
    parser.feed(html)

    assert len(parser.blocks) == 2

    block1, block2 = parser.blocks
    assert block1["id"].startswith("pyodide-block-")
    assert block2["id"].startswith("pyodide-block-")
    assert block1["id"] != block2["id"]


@pytest.mark.sphinx("html", testroot="pyodide")
def test_code_content_in_html(app: SphinxTestApp) -> None:
    """Code content appears in hidden pre.pyodide-code element."""
    app.build()
    html = (app.outdir / "index.html").read_text(encoding="utf-8")

    parser = _PyodideBlockParser()
    parser.feed(html)

    code = parser.blocks[0].get("code", "")
    assert 'print("hello")' in code


@pytest.mark.sphinx("html", testroot="pyodide")
def test_package_deps_in_html(app: SphinxTestApp) -> None:
    """Block with :packages: option has a deps script tag."""
    app.build()
    html = (app.outdir / "index.html").read_text(encoding="utf-8")

    parser = _PyodideBlockParser()
    parser.feed(html)

    deps = parser.blocks[1].get("deps", "")
    assert "numpy" in deps
    assert "packages" in deps


@pytest.mark.sphinx("html", testroot="pyodide")
def test_pygments_highlighting(app: SphinxTestApp) -> None:
    """Code is syntax-highlighted via Pygments (has span tags)."""
    app.build()
    html = (app.outdir / "index.html").read_text(encoding="utf-8")
    spans = re.findall(r"<span[^>]*>", html)
    assert len(spans) > 0


@pytest.mark.sphinx("html", testroot="pyodide")
def test_first_block_no_deps(app: SphinxTestApp) -> None:
    """First block (no :packages:) has no deps script tag."""
    app.build()
    html = (app.outdir / "index.html").read_text(encoding="utf-8")

    parser = _PyodideBlockParser()
    parser.feed(html)

    deps = parser.blocks[0].get("deps", "")
    assert deps == ""


@pytest.mark.sphinx("html", testroot="pyodide")
def test_pyodide_js_loaded_on_page(app: SphinxTestApp) -> None:
    """Page includes the Pyodide CDN script and our JS."""
    app.build()
    html = (app.outdir / "index.html").read_text(encoding="utf-8")
    assert "cdn.jsdelivr.net/pyodide" in html
    assert "sphinx_pyodide.js" in html


@pytest.mark.sphinx("html", testroot="pyodide")
def test_pyodide_css_loaded(app: SphinxTestApp) -> None:
    """Page includes the pyodide CSS."""
    app.build()
    html = (app.outdir / "index.html").read_text(encoding="utf-8")
    assert "sphinx_pyodide.css" in html


@pytest.mark.sphinx("html", testroot="pyodide")
def test_output_container_present(app: SphinxTestApp) -> None:
    """Each block has a pyodide-output container."""
    app.build()
    html = (app.outdir / "index.html").read_text(encoding="utf-8")
    assert html.count("pyodide-output") == 2
    assert html.count("pyodide-status") == 2


@pytest.mark.sphinx(
    "html",
    testroot="pyodide",
    confoverrides={"pyodide_build_output": True},
)
def test_build_output_captured(app: SphinxTestApp) -> None:
    """Build-time output capture populates noscript fallback."""
    app.build()
    html = (app.outdir / "index.html").read_text(encoding="utf-8")
    assert "pyodide-noscript-output" in html
    assert "hello" in html


@pytest.mark.sphinx(
    "html",
    testroot="pyodide-globals",
)
def test_shared_globals_between_blocks(app: SphinxTestApp) -> None:
    """Variable defined in first block is accessible in second block."""
    app.build()
    html = (app.outdir / "index.html").read_text(encoding="utf-8")
    assert "pyodide-noscript-output" in html
    assert "42" in html


@pytest.mark.sphinx(
    "html",
    testroot="pyodide-globals",
)
def test_setup_code_executed(app: SphinxTestApp) -> None:
    """setup-code runs before block code and its output is captured."""
    app.build()
    html = (app.outdir / "index.html").read_text(encoding="utf-8")
    assert "hello from setup" in html
