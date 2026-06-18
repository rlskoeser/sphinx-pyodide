# sphinx-pyodide

Sphinx extension to add a `pyodide` directive for embedding executable Python code blocks in documentation using Pyodide (Python in the browser via WebAssembly).

## Usage

```rst
.. pyodide::
    :show-output:

    print("Hello from Pyodide!")
    import numpy as np
    print(np.array([1, 2, 3]))
```

## Requirements

- Python 3.12+

## Installation

```bash
pip install sphinx-pyodide
```

## Development

### Setup

Create and activate a python virtual environment, and install
the package in editable mode with development dependencies.

```bash
uv venv --python 3.12
source .venv/bin/activate  # or `hatch shell`

uv pip install -e ".[dev]"
```

### Build

```bash
hatch build
```

### Linting & Type Checking

```bash
# Run ruff linter
ruff check src/

# Run ruff with auto-fix
ruff check src/ --fix

# Run ty type checker
ty check src/
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run all hooks
pre-commit run --all-files
```

### Testing

```bash
# Run all tests (when available)
hatch run test
```

### Running a Local Sphinx Build

```bash
cd /path/to/test-project
sphinx-build -b html . _build
```

## License

Apache 2.0
