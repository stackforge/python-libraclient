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



From PyPI
----------------------------
The :program:`python-libraclient` package is published on `PyPI`_ and so can be installed using the pip tool, which will manage installing all
python dependencies:

.. code-block:: shell-session

   pip install python-libraclient

*Warning: the packages on PyPI may lag behind the git repo in functionality.*


Setup the client from source
----------------------------
If you want the latest version, straight from github:

.. code-block:: shell-session

    git clone git@github.com:stackforge/python-libraclient.git
    cd python-libraclient
    virtualenv .venv
    . .venv/bin/activate
    pip install -r requirements.txt -r test-requirements.txt
    python setup.py install


Setup the client in development mode
------------------------------------

Installing in development mode allows your to make changes to the source code & test directly without having to re-run the "python setup.py install"
step.  You can find out more about `Development Mode`_

.. code-block:: shell-session

    git clone git@github.com:stackforge/python-libraclient.git
    cd python-libraclient
    virtualenv .venv
    . .venv/bin/activate
    pip install -r requirements.txt -r test-requirements.txt
    python setup.py develop

.. _Development Mode: http://pythonhosted.org/distribute/setuptools.html#development-mode
.. _PyPI: https://pypi.python.org/pypi/python-libraclient/