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


Directive Options
-----------------

``:packages:``
    Comma-separated list of packages to install before running code.

``:show-output:``
    Flag to display output (currently always shown).

``:editable:``
    Flag to make the code block editable (not yet implemented).

``:setup-code:``
    Reference code to run before the main block (not yet implemented).


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

    sphinx-build -b html docs/source docs/build
