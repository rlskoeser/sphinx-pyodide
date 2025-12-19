import hashlib
import json
import os
from importlib import resources

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer
from sphinx.application import Sphinx
from sphinx.util.fileutil import copy_asset

PYODIDE_JS_URL = "https://cdn.jsdelivr.net/pyodide/v0.29.0/full/pyodide.js"


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
    option_spec = {
        "show-output": directives.flag,
        "editable": directives.flag,
        "packages": directives.unchanged,
        "setup-code": directives.unchanged,
    }

    def run(self):
        code = "\n".join(self.content)
        # Generate unique ID for this code block
        code_id = hashlib.md5(code.encode()).hexdigest()[:8]

        node = PyodideNode()
        node["code"] = code
        node["code_id"] = code_id
        node["show_output"] = "show-output" in self.options
        node["editable"] = "editable" in self.options
        node["packages"] = [pkg.strip() for pkg in self.options.get("packages", "").split(',') if pkg.strip()]
        node["setup_code"] = self.options.get("setup-code", "")

        return [node]


def visit_pyodide_node_html(self, node):
    """Generate HTML for Pyodide code blocks."""
    print("visiting pyodide node")
    code = node["code"]
    code_id = node["code_id"]
    show_output = node["show_output"]   # ignored, currently assumed true
    editable = node["editable"]         # not currently supported
    packages = node["packages"]
    setup_code = node["setup_code"]     # suggested by claude, not yet supported
    # use pygments to highlight the code for display
    highlighted_code = highlight(code, PythonLexer(), HtmlFormatter())
    # if dependencies are specified, add json code with 
    # list of packages to install before running code
    deps = ""
    if packages:
        deps = """<script type="application/json" class="deps">""" + \
        json.dumps({'packages': packages}) + \
        "</script>"
    # create a block with optional dependencies, hidden code to run,
    # highlighted code for display, output container, and status
    html = f"""
    <div class="pyodide-block" id="pyodide-block-{code_id}">
    {deps}
    <pre class="pyodide-code" style="display: none;">{code}</pre>
    {highlighted_code}
    <pre class="pyodide-output"></pre>
    <div class="pyodide-status"></div>    
    """
    self.body.append(html)


def depart_pyodide_node_html(self, node):
    """End Pyodide HTML block."""
    self.body.append("</div>")


def copy_asset_files(app, exc):
    """Add sphinx-pyodide JavaScript and CSS files to static directory."""
    if exc is not None:  # build failed
        return
    asset_files = [
        resources.files('sphinx_pyodide') / 'sphinx_pyodide.js',
        resources.files('sphinx_pyodide') / 'sphinx_pyodide.css',        
    ]
    for path in asset_files:
        # Compatibility with Sphinx < 7.2 (Path would raise an exception)
        path = str(path)
        copy_asset(path, os.path.join(app.outdir, '_static'))


def add_assets(app, pagename, templatename, context, doctree):
    """Add sphinx Pyodide script and CSS to pages that use it."""
    if doctree and doctree.traverse(PyodideNode):
        app.add_js_file(PYODIDE_JS_URL)
        app.add_js_file("sphinx_pyodide.js")
        app.add_css_file("sphinx_pyodide.css")


def setup(app: Sphinx):
    """Setup the Sphinx extension."""
    app.add_node(PyodideNode, html=(visit_pyodide_node_html, depart_pyodide_node_html))
    app.add_directive("pyodide", PyodideDirective)
    app.connect("html-page-context", add_assets)
    app.connect('build-finished', copy_asset_files)

    return {
        "version": "0.1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
