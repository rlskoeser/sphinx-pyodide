# sphinx-pyodide

Sphinx extension to add a `pyodide` directive for embedding executable Python code blocks in documentation using Pyodide (Python in the browser via WebAssembly).

## Installation

```bash
pip install sphinx-pyodide
```

## Configuration

Add to your Sphinx `conf.py`:

```python
extensions = ["sphinx_pyodide"]
```

## Usage

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

```bash
uv sync --dev
```

### Linting & Type Checking

```bash
ruff check src/
ty check src/
```

### Pre-commit Hooks

```bash
pre-commit install
pre-commit run --all-files
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
sphinx-build -b html docs/source docs/build
```

## License

Apache 2.0
