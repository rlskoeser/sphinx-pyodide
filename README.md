# sphinx-pyodide

Sphinx extension to add a `pyodide` directive for embedding executable Python code blocks in documentation using [Pyodide](https://pyodide.org/en/stable/) (Python in the browser via WebAssembly).

## How to Use

Install with `pip`, `uv`, or similar:

```bash
pip install sphinx-pyodide
```

Enable the extension by including in your Sphinx `conf.py`:

```python
extensions = ["sphinx_pyodide"]
```

Use in documentation files.

```rst
.. pyodide::
    :show-output:

    print("Hello from Pyodide!")
    import numpy as np
    print(np.array([1, 2, 3]))
```

### Options

| Option          | Type   | Description                                                                                           |
| --------------- | ------ | ----------------------------------------------------------------------------------------------------- |
| `:packages:`    | string | Comma-separated PyPI packages to load (e.g., `numpy, pandas`). Local `.whl` files are also supported. |
| `:show-output:` | flag   | Display the output inline after the code block.                                                       |
| `:editable:`    | flag   | Allow users to edit the code before running.                                                          |
| `:setup-code:`  | string | Python code to run once before the main code (e.g., imports).                                         |

## Development

### Setup

Install development dependencies; install pre-commit hooks on first setup.

```bash
uv sync --dev
pre-commit install
```

### Testing

Tests use `sphinx.testing` fixtures via `pytest`.

```bash
pytest tests/
pytest tests/ -k test_name
pytest tests/ --cov=src/sphinx_pyodide
```

### Build Documentation

```bash
# One-time build
sphinx-build -b html docs/source docs/build

# Auto-reload with live preview (recommended for development)
sphinx-autobuild docs/source docs/build
```

**Note:** The pyodide blocks require an HTTP server to run (`file://`
will not work due to CORS). `sphinx-autobuild` serves on
`http://127.0.0.1:8000 <http://127.0.0.1:8000>`\_ by default.

## License

Apache 2.0
