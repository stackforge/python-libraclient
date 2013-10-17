Examples
========

Create Load Balancer
--------------------

.. code-block:: bash

   libra --os_auth_url=https://company.com/openstack/auth/url \
   --os_username=username --os_password=pasword --os_tenant_name=tenant \
   --os_region_name=region create --name=my_load_balancer \
   --node 192.168.1.1:80 --node 192.168.1.2:80

This example will create a basic load balancer which will listen on port 80 and
direct traffic in a round-robin fashion to two nodes, 192.168.1.1 and
192.168.1.2.  Both these nodes are web servers listening on port 80.  The Libra
Client will then return a table similar to the below:

+------------+----------------------------------------+
| Property   | Value                                  |
+------------+----------------------------------------+
| status     | BUILD                                  |
| updated    | 2013-10-31T11:59:24                    |
| protocol   | HTTP                                   |
| name       | test                                   |
| algorithm  | ROUND_ROBIN                            |
| created    | 2013-10-31T11:59:24                    |
| virtualIps | <VIP: 359 - PUBLIC IPV4 15.125.20.157> |
| port       | 80                                     |
| nodes      | <Node: 15.126.201.193:80>              |
|            | <Node: 15.126.201.70:80>               |
| id         | 80303                                  |
+------------+----------------------------------------+

Create a Load Balancer with Node Options
----------------------------------------

.. code-block:: bash

   libra --os_auth_url=https://company.com/openstack/auth/url \
   --os_username=username --os_password=pasword --os_tenant_name=tenant \
   --os_region_name=region create --name=my_load_balancer \
   --node 192.168.1.1:80:weight=1 --node 192.168.1.2:80:weight=2

Nearly identical to the above example, this creates a new load balancer
with two nodes, but one is more heavily weighted than the other, causing
it to accept more traffic.

Create a Shared Load Balancer
-----------------------------

It is possible for a single logical load balancer to balancer traffic for both
HTTP and HTTPS for a site.  For this example we will add an HTTPS load balancer
to the load balancer we created previously:

.. code-block:: bash

   libra --os_auth_url=https://company.com/openstack/auth/url \
   --os_username=username --os_password=pasword --os_tenant_name=tenant \
   --os_region_name=region create --name=my_load_balancer \
   --node 192.168.1.1:443 --node 192.168.1.2:443 --protocol=TCP --port=443 \
   --vip=52

We have taken the IP ID which was provided in the original create and given this
as a VIP number in the command.  We are also setting to TCP mode so the SSL
termination happens at the web server and set the load balancer to listen on
port 443.  The result is as follows:

+------------+----------------------------------------+
| Property   | Value                                  |
+------------+----------------------------------------+
| status     | BUILD                                  |
| updated    | 2013-10-31T11:59:24                    |
| protocol   | HTTP                                   |
| name       | test                                   |
| algorithm  | ROUND_ROBIN                            |
| created    | 2013-10-31T11:59:24                    |
| virtualIps | <VIP: 359 - PUBLIC IPV4 15.125.20.157> |
| port       | 80                                     |
| nodes      | <Node: 15.126.201.193:80>              |
|            | <Node: 15.126.201.70:80>               |
| id         | 80303                                  |
+------------+----------------------------------------+

Add a Node
----------

.. code-block:: bash

   libra --os_auth_url=https://company.com/openstack/auth/url \
   --os_username=username --os_password=pasword --os_tenant_name=tenant \
   --os_region_name=region node-add 158 --node=192.168.1.3:443

In this example we have take the ID of the load balancer of the previos example
to add a web server to.  The result should look something like this:

+----+-------------+------+-----------+--------+
| ID |   Address   | Port | Condition | Status |
+----+-------------+------+-----------+--------+
|    | 192.168.1.3 | 443  |           |        |
+----+-------------+------+-----------+--------+

