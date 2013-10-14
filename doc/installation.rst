.. _installation:

Installation
============

.. _install-ppa:

From Ubuntu Package via PPA
---------------------------

1. Install utility

::

    sudo apt-get install python-software-properties

2. Add the PPA

::

    sudo apt-add-repository ppa:libra-core/ppa

3. Update the package indexes

::

    sudo apt-get update

4. Install packages

::

    sudo apt-get install python-libraclient


.. _install-pypi:

From PyPI
---------

The :program:`python-libraclient` package is published on `PyPI <https://pypi.python.org/pypi/python-libraclient/>`_ and so can be installed using the pip tool, which will manage installing all
python dependencies.

.. note:: The pip tool isn't bundled by default with some versions of the different distributions, please install it typically using a package manager for the platform you use.

.. note:: Needs to be done in a Virtual Environment or as root.

.. code-block:: shell-session

   pip install python-libraclient

.. warning::

    The packages on PyPI may lag behind the git repo in functionality.

.. _install-source:

Setup the client from source
----------------------------
If you want the latest version, straight from github:

.. code-block:: shell-session

    git clone git@github.com:stackforge/python-libraclient.git
    cd python-libraclient
    virtualenv .venv
    source .venv/bin/activate
    pip install -r requirements.txt -r test-requirements.txt
    python setup.py install


.. _install-development:

Setup the client in development mode
------------------------------------
Installing in development mode allows your to make changes to the source code & test directly without having to re-run the "python setup.py install"
step. You can find out more about this in the `Development Mode <http://pythonhosted.org/distribute/setuptools.html#development-mode>`_ online docs.

.. code-block:: shell-session

    git clone git@github.com:stackforge/python-libraclient.git
    cd python-libraclient
    virtualenv .venv
    source .venv/bin/activate
    pip install -r requirements.txt -r test-requirements.txt
    python setup.py develop

