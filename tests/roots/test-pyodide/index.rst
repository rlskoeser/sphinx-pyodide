Test pyodide
============

Basic block
~~~~~~~~~~~

.. pyodide::

    print("hello")


With packages
~~~~~~~~~~~~~

.. pyodide::
    :packages: numpy

    import numpy as np
    print(np.array([1, 2, 3]))
