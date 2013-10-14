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

From Ubuntu Package - donwloaded deb
------------------------------------

.. code-block:: bash

   sudo apt-get install python-pip
   sudo pip install python-novaclient --upgrade
   sudo dpkg -i python-libraclient_1.2.2-1_all.deb

If the last command fails with an unmet dependency run this to fix it:

.. code-block:: bash

   sudo apt-get -fy install


From Source
-----------

The python-setuptools package needs to be installed on your system before
installing the client from source.

.. code-block:: bash

    apt-get install python-pip
    pip install https://github.com/stackforge/python-libraclient/archive/master.zip#egg=libraclient