sphinx-pyodide
==============

.. toctree::
   :hidden:

   changelog

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

Build-time output is displayed as static output below each block.
Interactive execution requires opt-in — click **Enable Interactive**
to load Pyodide and run blocks live in the browser:

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


.. _shared-context:

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

Define named output for use as static output. The content
is stored in the build environment and referenced by the
``:output:`` option on ``pyodide`` directives. It is displayed
until the user enables interactive execution.

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
    Static output displayed in the output panel.
    Typically the expected output of the code block.
    Use ``\n`` for multi-line, or reference a named output block
    defined with the :ref:`pyodide-output-directive` directive.
    The static output is replaced when the user enables interactive
    execution.

    .. code-block:: rst

        .. pyodide::
            :output: Hello, world!

            print("Hello, world!")

    .. code-block:: rst

        .. pyodide::
            :output: Hello\nfrom\nPyodide!

            print("Hello\nfrom\nPyodide!")

``:show-errors:``
    Flag to display runtime errors in this block's live browser output.
    Errors are still logged to the console regardless.

    .. code-block:: rst

        .. pyodide::
            :show-errors:

            print(1 / 0)

    Overrides the global ``pyodide_show_errors`` setting for this
    block.

``:editable:``
    Flag to make the code block editable. Users can modify the code
    directly in the browser before clicking **▶ Run**.

``:setup-code:``
    Reference code to run before the main block. Useful for defining
    helper functions or imports used across multiple blocks (via
    :ref:`shared context <shared-context>`).

    .. code-block:: rst

        .. pyodide::
            :setup-code: import math

            print(math.pi)

    The setup code runs in the same namespace as the block code and
    any earlier blocks on the page.

Configuration
-------------

``pyodide_build_output``
    Execute code at build time and capture stdout as static output.
    Defaults to ``True``.

    .. code-block:: python

        pyodide_build_output = False

    When enabled (default), any ``pyodide`` block without an explicit
    ``:output:`` option runs during ``sphinx-build``. The printed output
    is displayed in the output panel and remains visible until the user
    enables interactive execution. Clicking **Enable Interactive** runs
    the code live in Pyodide and replaces the static output.

    If the code raises an exception at build time, the error message
    and traceback are captured and displayed with a ``[Build-time error]``
    label and distinct styling.

    Set to ``False`` to disable build-time capture. Blocks will show
    an empty output panel until the user enables interactive mode.

``pyodide_show_errors``
    Show runtime errors in the live browser output.
    Defaults to ``False``.

    .. code-block:: python

        pyodide_show_errors = True

    When ``False`` (default), errors in ``pyodide`` blocks are
    only logged to the browser console. Set to ``True`` to
    display them in the output panel alongside successful
    results.

    Can be overridden per-block with the ``:show-errors:``
    directive option.

``pyodide_enable_text``
    HTML content for the enable banner note displayed before the
    first ``pyodide`` block. Defaults to a message describing the
    interactive blocks and static output. May contain HTML links.

    .. code-block:: python

        pyodide_enable_text = 'Run code in the browser via <a href="https://pyodide.org/">Pyodide</a>.'

``pyodide_noscript_text``
    Text for the noscript fallback banner, shown when JavaScript is
    disabled.

    .. code-block:: python

        pyodide_noscript_text = "Interactive code blocks require JavaScript."


Development
-----------

.. code-block:: bash

    git clone https://github.com/your-org/sphinx-pyodide
    cd sphinx-pyodide
    uv sync --dev

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
