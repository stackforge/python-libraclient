Installation
============

From Ubuntu Package
-------------------

.. code-block:: bash

   sudo apt-get install python-pip
   sudo pip install python-novaclient requests --upgrade
   sudo dpkg -i python-libraclient_1.2-1_all.deb

If the last command fails with an unmet dependency run this to fix it:

.. code-block:: bash

   sudo apt-get -fy install

From Source
-----------

The python-setuptools package needs to be installed on your system before
installing the client from source.

.. code-block:: bash

   sudo apt-get install python-setuptools
   sudo python setup.py install
