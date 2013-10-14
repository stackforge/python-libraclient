.. _installation:

Installation
============

From Ubuntu Package via PPA
---------------------------

1. Install utility

::

    apt-get install python-software-properties

2. Add the PPA

::

    apt-add-repository ppa:libra-core/ppa

3. Update the package indexes

::

    apt-get update -q

4. Install packages

::

    apt-get install -qy python-libraclient


.. _virtual-env:

Virtual Environment
-------------------

.. code-block:: bash

  virtualenv $HOME/libraclient_venv
  . $HOME/libraclient_venv/bin/activate


From Source
-----------

See :ref:`virtual-env` if you want to install this isolated to your
python libraries.

.. code-block:: bash

    apt-get install python-pip
    pip install -e git+https://github.com/stackforge/python-libraclient#egg=libraclient


From PyPI (Python Package Index)
--------------------------------

See :ref:`virtual-env` if you want to install this isolated to your
python libraries.

.. code-block:: bash

  apt-get install python-pip