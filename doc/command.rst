Usage
=====

Synopsis
--------

:program:`libra_client` [:ref:`GENERAL OPTIONS <libra_client-options>`] [:ref:`COMMAND <libra_client-commands>`] [*COMMAND_OPTIONS*]

Description
-----------

:program:`libra_client` is a utility designed to communicate with Atlas API
based Load Balancer as a Service systems.

.. _libra_client-options:

Global Options
--------------

.. program:: libra_client

.. option:: --help, -h

   Show help message and exit

.. option:: --debug

   Turn on HTTP debugging for requests

.. option:: --insecure

   Don't validate SSL certs

.. option:: --bypass_url <bypass-url>

   URL to use as an endpoint instead of the one specified by the Service
   Catalog

.. option:: --service_type <service-type>

   Alternative service type to use for your cloud provider (default is
   'hpext:lbaas')

.. option:: --os_auth_url <auth-url>

   The OpenStack authentication URL.  Default is ``OS_AUTH_URL`` or
   ``LIBRA_URL`` environment variables

.. option:: --os_username <auth-user-name>

   The user name to use for authentication.  Default is ``OS_USERNAME`` or
   ``LIBRA_USERNAME`` environment variables

.. option:: --os_password <auth-password>

   The password to use for authentication.  Default is ``OS_PASSWORD`` or
   ``LIBRA_PASSWORD`` environment variables

.. option:: --os_tenant_name <auth-tenant-name>

   The tenant to authenticate to.  Default is ``OS_TENANT_NAME`` or
   ``LIBRA_PROJECT_ID`` environment variables

.. option:: --os_region_name <region-name>

   The region the load balancer is located.  Default is ``OS_REGION_NAME`` or
   ``LIBRA_REGION_NAME`` environment variables

.. _libra_client-commands:

Client Commands
---------------

.. program:: libra_client algorithms

algorithms
^^^^^^^^^^

Gets a list of supported algorithms

.. program:: libra_client create

create
^^^^^^

Create a load balancer

.. option:: --name <name>

   The name of the node to be created

.. option:: --port <port>

   The port the load balancer will listen on

.. option:: --protocol <protocol>

   The protocol type for the load balancer (HTTP, TCP or GALERA).
   The Galera option adds support for deadlock avoidance in Galera clusters,
   see `Serveral Nine's Blog <http://www.severalnines.com/blog/avoiding-deadlocks-galera-set-haproxy-single-node-writes-and-multi-node-reads>`_ on this.

.. option:: --node <ip:port>

   The IP and port for a load balancer node (can be used multiple times to add multiple nodes)

.. option:: --vip <vip>

   The virtual IP ID of an existing load balancer to attach to

.. program:: libra_client delete

delete
^^^^^^

Delete a load balancer

.. option:: --id <id>

   The ID of the load balancer

.. program:: libra_client limits

limits
^^^^^^

Show the API limits for the user

.. program:: libra_client list

list
^^^^

List all load balancers

.. option:: --deleted

   Show deleted load balancers

.. program:: libra_client logs

logs
^^^^

Send a snapshot of logs to an object store

.. option:: --id <id>

   The ID of the load balancer

.. option:: --storage <store>

   Storage type

.. option:: --endpoint <endpoint>

   Object store endpoint to use

.. option:: --basepath <basepath>

   Object store based directory

.. option:: --token <token>

   Object store authentication token

.. program:: libra_client modify

modify
^^^^^^

Update a load balancer's configuration

.. option:: --id <id>

   The ID of the load balancer

.. option:: --name <name>

   A new name for the load balancer

.. option:: --algorithm <algorithm>

   A new algorithm for the load balancer

.. program:: libra_client monitor-list

monitor-list
^^^^^^^^^^^^

List the health monitor for a load balancer

.. option:: --id <id>

   The ID of the load balancer

.. program:: libra_client monitor-delete

monitor-delete
^^^^^^^^^^^^^^

Delete the health monitor for a load balancer

.. option:: --id <id>

   The ID of the load balancer

.. program:: libra_client monitor-modify

monitor-modify
^^^^^^^^^^^^^^

Modify the health monitor for a load balancer

.. option:: --id <id>

   The ID of the load balancer

.. program:: libra_client node-add

node-add
^^^^^^^^

Add a node to a load balancer

.. option:: --id <id>

   The ID of the load balancer

.. option:: --node <ip:port>

   The node address in ip:port format (can be used multiple times to add multiple nodes)

.. program:: libra_client node-delete

node-delete
^^^^^^^^^^^

Delete a node from the load balancer

.. option:: --id <id>

   The ID of the load balancer

.. option:: --nodeid <nodeid>

   The ID of the node to be removed

.. program:: libra_client node-list

node-list
^^^^^^^^^

List the nodes in a load balancer

.. option:: --id <id>

   The ID of the load balancer

.. program:: libra_client node-modify

node-modify
^^^^^^^^^^^

Modify a node's state in a load balancer

.. option:: --id <id>

   The ID of the load balancer

.. option:: --nodeid <nodeid>

   The ID of the node to be modified

.. option:: --condition <condition>

   The new state of the node (either ENABLED or DISABLED)

.. program:: libra_client node-status

node-status
^^^^^^^^^^^

Get the status of a node in a load balancer

.. option:: --id <id>

   The ID of the load balancer

.. option:: --nodeid <nodeid>

   The ID of the node in the load balancer
.. program:: libra_client protocols

protocols
^^^^^^^^^

Gets a list of supported protocols

.. program:: libra_client status

status
^^^^^^

Get the status of a single load balancer

.. option:: --id <id>

   The ID of the load balancer

virtualips
^^^^^^^^^^

Get a list of virtual IPs

.. option:: --id <id>

   The ID of the load balancer
