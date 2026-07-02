# Changelog

## 0.1.1 — 2026-07-02

- Remove stray quote in WebAssembly link in interactive notice
- Fix error in python-publish github actions workflow

## 0.1.0 — 2026-07-02

Initial release of `sphinx-pyodide`, a Sphinx extension for embedding
executable Python code blocks in documentation via Pyodide.

### Features

- **`pyodide` directive** — embed Python code blocks that run live in
    the browser via Pyodide (WebAssembly)
- **Opt-in execution** — Pyodide is not loaded automatically; a
    `note` admonition with an **Enable Interactive** button appears
    before the first block
- **Build-time output** — code executes during `sphinx-build`;
    captured stdout is displayed as static output until the user enables
    interactive mode (configurable via `pyodide_build_output`)
- **Package installation** — install PyPI packages (e.g., `numpy`)
    before execution with the `:packages:` option; local `.whl` files
    are also supported
- **Editable blocks** — `:editable:` flag makes code blocks
    contenteditable so users can modify and re-run code
- **Sequential shared context** — all blocks on a page share a single
    Python interpreter; variables and state persist across blocks in
    document order
- **`pyodide-output` directive** — define named static output for
    use as fallback content
- **Error handling** — `:show-errors:` flag or global
    `pyodide_show_errors` config displays runtime errors in the output
    panel; build-time errors are captured with distinct styling
- **Setup code** — `:setup-code:` option runs Python before the
    main block (useful for shared imports or helpers)
- **Configurable banner text** — `pyodide_enable_text` and
    `pyodide_noscript_text` allow custom HTML content in the enable
    banner and noscript fallback
- **Light/dark mode** — respects `prefers-color-scheme` and
    explicit `data-theme` attributes
- **Syntax highlighting** — code is highlighted via Pygments

### Directive options

- `:packages:` — comma-separated PyPI packages or `.whl` paths
- `:editable:` — allow editing code before running
- `:output:` — static output text (`\n` for newlines)
- `:show-errors:` — display runtime errors in the output panel
- `:setup-code:` — Python code to run before the main block

### Configuration

- `pyodide_build_output` — capture stdout at build time (default `True`)
- `pyodide_show_errors` — show runtime errors in output (default `False`)
- `pyodide_enable_text` — HTML for the enable banner note
- `pyodide_noscript_text` — text for the noscript fallback banner
