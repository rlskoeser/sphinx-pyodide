sphinx-pyodide
==============

``sphinx-pyodide`` is a Sphinx extension that adds a ``pyodide`` directive
for embedding **executable Python code blocks** in documentation. Code runs
in the browser via `Pyodide <https://pyodide.org/>`_ (CPython compiled to
WebAssembly).

Installation
------------

.. code-block:: bash

    pip install sphinx-pyodide

Enable in ``conf.py``:

.. code-block:: python

    extensions = ["sphinx_pyodide"]

Usage
-----

Basic executable block
~~~~~~~~~~~~~~~~~~~~~~

Write a ``.. pyodide::`` directive with the Python code as content:

.. code-block:: rst

    .. pyodide::

        print("Hello from Pyodide!")

It renders as an executable block in the browser:

.. pyodide::

    print("Hello from Pyodide!")


With output display
~~~~~~~~~~~~~~~~~~~

.. code-block:: rst

    .. pyodide::

        import sys
        print(f"Python {sys.version}")

.. pyodide::

    import sys
    print(f"Python {sys.version}")


Installing packages
~~~~~~~~~~~~~~~~~~~

Use the ``:packages:`` option to install packages via micropip before
running the code.

.. code-block:: rst

    .. pyodide::
        :packages: numpy

        import numpy as np
        arr = np.array([1, 2, 3, 4, 5])
        print(f"mean = {arr.mean()}, sum = {arr.sum()}")

.. pyodide::
    :packages: numpy

    import numpy as np
    arr = np.array([1, 2, 3, 4, 5])
    print(f"mean = {arr.mean()}, sum = {arr.sum()}")


Multiple packages
~~~~~~~~~~~~~~~~~

.. code-block:: rst

    .. pyodide::
        :packages: numpy, pytz

        from datetime import datetime
        import pytz
        tz = pytz.timezone("America/New_York")
        now = datetime.now(tz)
        print(f"New York time: {now.strftime('%H:%M:%S')}")

.. pyodide::
    :packages: numpy, pytz

    from datetime import datetime
    import pytz
    tz = pytz.timezone("America/New_York")
    now = datetime.now(tz)
    print(f"New York time: {now.strftime('%H:%M:%S')}")


Shared context
~~~~~~~~~~~~~~

All ``.. pyodide::`` blocks on the same page share a single Python
interpreter. Blocks execute **sequentially and in document order**
— each block finishes before the next one starts. Variables, imports,
and state defined in one block persist and are available to later
blocks.

.. code-block:: rst

    .. pyodide::

        x = 42

    .. pyodide::

        print(x * 2)  # accesses x from the block above; prints 84

Directives
----------

.. pyodide::
    :packages: sphinx_pyodide

    from sphinx_pyodide.main import PyodideDirective, PyodideOutputDirective
    print("directives loaded")

``pyodide``
~~~~~~~~~~~

The main directive for embedding executable Python code.

.. code-block:: rst

    .. pyodide::
        :packages: numpy
        :editable:

        import numpy as np
        print(np.array([1, 2, 3]))

.. _pyodide-output-directive:

``pyodide-output``
~~~~~~~~~~~~~~~~~~

Define named output for use as a noscript fallback. The content
is stored in the build environment and referenced by the
``:output:`` option on ``pyodide`` directives.

.. code-block:: rst

    .. pyodide-output:: my-output

        Hello
        from
        Pyodide!

    .. pyodide::
        :output: my-output

        print("Hello\\nfrom\\nPyodide!")

The ``pyodide-output`` directive must appear before the
``pyodide`` directive that references it.

Options
-------

``:packages:``
    Comma-separated list of packages to install before running code.
    Entries ending in ``.whl`` are treated as **local wheel files** —
    paths are resolved relative to the source document and the files
    are copied into the built site automatically.

    .. code-block:: rst

        .. pyodide::
            :packages: numpy, ./wheels/mylib-1.0-py3-none-any.whl

            import mylib
            mylib.hello()

    Place ``.whl`` files in a ``wheels/`` directory next to your source
    document (e.g., ``docs/source/wheels/``). They are copied into the
    built site automatically.

    Transitive PyPI dependencies declared in the wheel's metadata are
    resolved automatically by ``micropip`` at runtime.

    **Tip:** To generate wheels for packages not on PyPI:

    .. code-block:: bash

        # Your own package only
        uv build --wheel

        # Your package + all its dependencies
        uv pip wheel . -w wheels/

        # Third-party package (download wheel from PyPI)
        uv pip wheel requests -w wheels/

    The resulting ``.whl`` files are placed in ``dist/`` (uv build) or
    ``wheels/`` (pip wheel) by default.

``:output:``
    Static output shown as a fallback when JavaScript is disabled.
    Typically the expected output of the code block.
    Use ``\n`` for multi-line, or reference a named output block
    defined with the :ref:`pyodide-output-directive` directive.

    .. code-block:: rst

        .. pyodide::
            :output: Hello, world!

            print("Hello, world!")

    .. code-block:: rst

        .. pyodide::
            :output: Hello\nfrom\nPyodide!

            print("Hello\nfrom\nPyodide!")

``:editable:``
    Flag to make the code block editable (not yet implemented).

``:setup-code:``
    Reference code to run before the main block (not yet implemented).

Configuration
-------------

``pyodide_build_output``
    Execute code at build time and capture stdout as the
    :ref:`noscript fallback output <pyodide-output-directive>`.
    Set to ``True`` in ``conf.py`` to enable.

    .. code-block:: python

        pyodide_build_output = True

    When enabled, any ``pyodide`` block without an explicit
    ``:output:`` option runs during ``sphinx-build`` and its
    printed output is used as the static noscript fallback.


Development
-----------

.. code-block:: bash

    git clone https://github.com/your-org/sphinx-pyodide
    cd sphinx-pyodide
    uv venv --python 3.12
    source .venv/bin/activate
    uv pip install -e ".[dev]"

Build these docs:

.. code-block:: bash

    # Build once
    sphinx-build -b html docs/source docs/build

    # Auto-reload with live preview (recommended)
    sphinx-autobuild docs/source docs/build

Open http://localhost:8000 in your browser. An HTTP server is
required for local wheel dependencies, since micropip can not install
from ``file://`` URLs due to CORS.  (For projects without local wheels,
browsing static html is probably be sufficient.)
