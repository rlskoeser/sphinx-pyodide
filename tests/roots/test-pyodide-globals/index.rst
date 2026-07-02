Test pyodide shared globals
===========================

Define a variable
~~~~~~~~~~~~~~~~~

.. pyodide::

    x = 42

Use that variable
~~~~~~~~~~~~~~~~~

.. pyodide::

    print(x)

With setup-code
~~~~~~~~~~~~~~~

.. pyodide::
    :setup-code: val = "hello from setup"

    print(val)
