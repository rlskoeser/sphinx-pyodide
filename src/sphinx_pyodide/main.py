"""Sphinx extension for embedding executable Python code via Pyodide."""

import hashlib
import json
from importlib import resources
from pathlib import Path
from typing import Any, ClassVar

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.python import PythonLexer
from sphinx.application import Sphinx
from sphinx.util.fileutil import copy_asset

PYODIDE_JS_URL = "https://cdn.jsdelivr.net/pyodide/v0.29.4/full/pyodide.js"


class PyodideNode(nodes.General, nodes.Element):
    """Custom node for Pyodide code blocks."""


class PyodideDirective(Directive):
    """
    Directive for embedding executable Python code using Pyodide.

    Usage:
        .. pyodide::
            :show-output: true
            :editable: true

            print("Hello from Pyodide!")
            import numpy as np
            print(np.array([1, 2, 3]))
    """

    has_content = True
    option_spec: ClassVar[dict[str, Any]] = {
        "show-output": directives.flag,
        "editable": directives.flag,
        "packages": directives.unchanged,
        "setup-code": directives.unchanged,
    }

    def run(self) -> list[PyodideNode]:
        """Create Pyodide node from directive content and options."""
        code = "\n".join(self.content)
        code_id = hashlib.md5(code.encode()).hexdigest()[:8]

        node = PyodideNode()
        node["code"] = code
        node["code_id"] = code_id
        node["show_output"] = "show-output" in self.options
        node["editable"] = "editable" in self.options
        node["packages"] = [
            pkg.strip()
            for pkg in self.options.get("packages", "").split(",")
            if pkg.strip()
        ]
        node["setup_code"] = self.options.get("setup-code", "")

        return [node]


def visit_pyodide_node_html(self: object, node: PyodideNode) -> None:
    """Generate HTML for Pyodide code blocks."""
    code = node["code"]
    code_id = node["code_id"]
    packages = node["packages"]
    highlighted_code = highlight(code, PythonLexer(), HtmlFormatter())

    deps = ""
    if packages:
        deps = (
            """<script type="application/json" class="deps">"""
            + json.dumps({"packages": packages})
            + "</script>"
        )

    html = f"""
    <div class="pyodide-block" id="pyodide-block-{code_id}">
    {deps}
    <pre class="pyodide-code" style="display: none;">{code}</pre>
    {highlighted_code}
    <pre class="pyodide-output"></pre>
    <div class="pyodide-status"></div>
    """
    self.body.append(html)  # type: ignore[attr-defined]


def depart_pyodide_node_html(self: object, node: PyodideNode) -> None:
    """End Pyodide HTML block."""
    self.body.append("</div>")  # type: ignore[attr-defined]


def copy_asset_files(app: Sphinx, exc: Exception | None) -> None:
    """Add sphinx-pyodide JavaScript and CSS files to static directory."""
    if exc is not None:
        return
    static_dir = str(Path(app.outdir) / "_static")
    package = resources.files("sphinx_pyodide")
    for name in ("sphinx_pyodide.js", "sphinx_pyodide.css"):
        copy_asset(str(package / name), static_dir)


def add_assets(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, Any],
    doctree: nodes.document,
) -> None:
    """Add sphinx Pyodide script and CSS to pages that use it."""
    if doctree and doctree.traverse(PyodideNode):
        app.add_js_file(PYODIDE_JS_URL)
        app.add_js_file("sphinx_pyodide.js")
        app.add_css_file("sphinx_pyodide.css")


def setup(app: Sphinx) -> dict[str, bool | str]:
    """Setup the Sphinx extension."""
    app.add_node(PyodideNode, html=(visit_pyodide_node_html, depart_pyodide_node_html))
    app.add_directive("pyodide", PyodideDirective)
    app.connect("html-page-context", add_assets)
    app.connect("build-finished", copy_asset_files)

    return {
        "version": "0.1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
