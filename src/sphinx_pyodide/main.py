"""Sphinx extension for embedding executable Python code via Pyodide."""

import hashlib
import io
import json
import sys
import traceback
from html import escape as html_escape
from pathlib import Path
from typing import Any, ClassVar

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.python import PythonLexer
from sphinx.application import Sphinx
from sphinx.util.fileutil import copy_asset

from sphinx_pyodide import __version__

PYODIDE_JS_URL = "https://cdn.jsdelivr.net/pyodide/v314.0.2/full/pyodide.js"

_doc_globals: dict[str, dict[str, object]] = {}


class PyodideNode(nodes.General, nodes.Element):
    """Custom node for Pyodide code blocks."""


class PyodideOutputNode(nodes.Element, nodes.General):
    """Node for named output blocks used as noscript fallback."""


def _skip_node(self: object, node: nodes.Element) -> None:
    """Skip rendering for nodes that only store data."""
    raise nodes.SkipNode


class PyodideOutputDirective(Directive):
    """Store named output content for use as noscript fallback."""

    has_content = True
    required_arguments = 1

    def run(self) -> list[PyodideOutputNode]:
        """Store content in environment for later use by pyodide directives."""
        env = self.state.document.settings.env
        if not hasattr(env, "pyodide_outputs"):
            env.pyodide_outputs = {}
        env.pyodide_outputs[self.arguments[0]] = "\n".join(self.content)
        return [PyodideOutputNode()]


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
        "editable": directives.flag,
        "output": directives.unchanged,
        "packages": directives.unchanged,
        "setup-code": directives.unchanged,
        "show-errors": directives.flag,
    }

    def run(self) -> list[PyodideNode]:
        """Create Pyodide node from directive content and options."""
        code = "\n".join(self.content)
        code_id = hashlib.md5(code.encode()).hexdigest()[:8]

        node = PyodideNode()
        node["code"] = code
        node["code_id"] = code_id
        node["editable"] = "editable" in self.options
        node["packages"] = [
            pkg.strip()
            for pkg in self.options.get("packages", "").split(",")
            if pkg.strip()
        ]
        node["setup_code"] = self.options.get("setup-code", "")

        output_val = self.options.get("output", "")
        env = self.state.document.settings.env
        node["show_errors"] = "show-errors" in self.options or getattr(
            env.config, "pyodide_show_errors", False
        )
        if hasattr(env, "pyodide_outputs") and output_val in env.pyodide_outputs:
            node["output"] = env.pyodide_outputs[output_val]
        elif output_val:
            node["output"] = output_val
        elif getattr(env.config, "pyodide_build_output", False):
            docname = env.docname
            if docname not in _doc_globals:
                _doc_globals[docname] = {
                    "__builtins__": __builtins__,
                    "__name__": "__main__",
                }
            globals_dict = _doc_globals[docname]

            setup_code = self.options.get("setup-code", "")
            if setup_code:
                try:
                    exec(setup_code, globals_dict)
                except Exception as exc:
                    msg = f"pyodide build-time setup-code failed: {exc}"
                    self.state.document.reporter.warning(msg, line=self.lineno)

            captured = io.StringIO()
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = captured
            sys.stderr = captured
            try:
                exec(code, globals_dict)
                node["output"] = captured.getvalue().rstrip("\n")
            except Exception:
                output = captured.getvalue()
                if output:
                    output += "\n"
                output += traceback.format_exc()
                node["output"] = output.rstrip("\n")
                node["has_error"] = True
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
        else:
            node["output"] = ""

        doc_source = self.state.document.get("source", "")
        doc_dir = Path(doc_source).parent if doc_source else Path()

        packages = []
        local_packages = {}
        for entry in node["packages"]:
            if entry.endswith(".whl"):
                src_path = (doc_dir / entry).resolve()
                dest_name = src_path.name
                local_packages[dest_name] = src_path
                env = self.state.document.settings.env
                if not hasattr(env, "pyodide_local_packages"):
                    env.pyodide_local_packages = {}
                env.pyodide_local_packages.setdefault(str(src_path), dest_name)
            else:
                packages.append(entry)

        node["packages"] = packages
        node["local_packages"] = list(local_packages.keys())

        return [node]


def visit_pyodide_node_html(self: object, node: PyodideNode) -> None:
    """Generate HTML for Pyodide code blocks."""
    code = node["code"]
    code_id = node["code_id"]
    packages = node["packages"]
    local_packages = node["local_packages"]
    output = node.get("output", "")
    show_errors = node.get("show_errors", False)
    show_errors_attr = ' data-show-errors="true"' if show_errors else ""
    highlighted_code = highlight(code, PythonLexer(), HtmlFormatter())

    install_list = packages + [f"/_static/pyodide-wheels/{w}" for w in local_packages]

    deps = ""
    if install_list:
        deps = (
            """<script type="application/json" class="deps">"""
            + json.dumps({"packages": install_list})
            + "</script>"
        )

    noscript_output = ""
    if output:
        escaped = html_escape(output.replace("\\n", "\n"))
        if node.get("has_error"):
            escaped = "[Build-time error]\n" + escaped
            cls = "pyodide-noscript-output pyodide-noscript-error"
        else:
            cls = "pyodide-noscript-output"
        noscript_output = f'<pre class="{cls}">{escaped}</pre>'

    if node["editable"]:
        highlighted_code = highlighted_code.replace(
            '<div class="highlight">',
            '<div class="highlight" contenteditable="true" spellcheck="false">',
        )
        editor = ""
        run_button = """<button class="pyodide-run-button">▶ Run</button>"""
    else:
        editor = f'<pre class="pyodide-code" style="display: none;">{code}</pre>'
        run_button = ""

    html = f"""
    <div class="pyodide-block" id="pyodide-block-{code_id}"{show_errors_attr}>
    {deps}
    {editor}
    {highlighted_code}
    <pre class="pyodide-output"></pre>
    <div class="pyodide-status">{run_button}</div>
    <noscript>
    {noscript_output}
    </noscript>
    """
    self.body.append(html)  # type: ignore[attr-defined]


def depart_pyodide_node_html(self: object, node: PyodideNode) -> None:
    """End Pyodide HTML block."""
    self.body.append("</div>")  # type: ignore[attr-defined]


def copy_static_assets(app: Sphinx) -> None:
    """Copy sphinx-pyodide JS and CSS to output _static directory."""
    _doc_globals.clear()
    static_dir = Path(app.outdir) / "_static"
    static_dir.mkdir(parents=True, exist_ok=True)
    package_dir = Path(__file__).parent
    for name in ("sphinx_pyodide.js", "sphinx_pyodide.css"):
        copy_asset(str(package_dir / name), str(static_dir), force=True)


def copy_asset_files(app: Sphinx, exc: Exception | None) -> None:
    """Copy local wheel files to the static directory."""
    if exc is not None:
        return
    wheels_dir = str(Path(app.outdir) / "_static" / "pyodide-wheels")
    env = getattr(app.env, "pyodide_local_packages", {})
    for src_path, dest_name in env.items():
        dest = Path(wheels_dir) / dest_name
        dest.parent.mkdir(parents=True, exist_ok=True)
        copy_asset(src_path, str(dest.parent), force=True)


def add_assets(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, Any],
    doctree: nodes.document,
) -> None:
    """Add sphinx Pyodide script and CSS to pages that use it."""
    if doctree and next(doctree.findall(PyodideNode), None) is not None:
        app.add_js_file(PYODIDE_JS_URL)
        app.add_js_file("sphinx_pyodide.js")
        app.add_css_file("sphinx_pyodide.css")

        msg = "This page contains interactive Python code blocks that require JavaScript to execute."
        if app.config.pyodide_build_output:
            msg += " Static output is displayed below for reference."
        else:
            msg += " The code blocks will not run without JavaScript."
        banner = (
            f'<noscript><div class="pyodide-noscript-banner">{msg}</div></noscript>'
        )
        doctree.insert(0, nodes.raw("", banner, format="html"))


def setup(app: Sphinx) -> dict[str, bool | str]:
    """Setup the Sphinx extension."""
    app.add_config_value("pyodide_build_output", default=True, rebuild="env")
    app.add_config_value("pyodide_show_errors", default=False, rebuild="env")
    app.add_node(PyodideNode, html=(visit_pyodide_node_html, depart_pyodide_node_html))
    app.add_node(PyodideOutputNode, html=(_skip_node, None))
    app.add_directive("pyodide", PyodideDirective)
    app.add_directive("pyodide-output", PyodideOutputDirective)
    app.connect("builder-inited", copy_static_assets)
    app.connect("html-page-context", add_assets)
    app.connect("build-finished", copy_asset_files)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
