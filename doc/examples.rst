Examples
========

Create Load Balancer
--------------------

.. code-block:: bash

   libra_client --os_auth_url=https://company.com/openstack/auth/url \
   --os_username=username --os_password=pasword --os_tenant_name=tenant \
   --os_region_name=region create --name=my_load_balancer \
   --node 192.168.1.1:80 --node 192.168.1.2:80

This example will create a basic load balancer which will listen on port 80 and
direct traffic in a round-robin fashion to two nodes, 192.168.1.1 and
192.168.1.2.  Both these nodes are web servers listening on port 80.  The Libra
Client will then return a table similar to the below:

+------+------------------+----------+------+-------------+--------+-------------------+-------------------+
|  ID  |       Name       | Protocol | Port |  Algorithm  | Status |      Created      |      Updated      |
+------+------------------+----------+------+-------------+--------+-------------------+-------------------+
| 1157 | my_load_balancer |   HTTP   |  80  | ROUND_ROBIN | BUILD  | 2013-01-10T14:41Z | 2013-01-10T14:41Z |
+------+------------------+----------+------+-------------+--------+-------------------+-------------------+

+--------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                                            IPs                                             |                                                                                                            Nodes                                                                                                             |
+--------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| [{u'ipVersion': u'IPV_4', u'type': u'PUBLIC', u'id': u'52', u'address': u'15.185.224.62'}] | [{u'status': u'ONLINE', u'id': u'2311', u'port': u'80', u'condition': u'ENABLED', u'address': u'192.168.1.1'}, {u'status': u'ONLINE', u'id': u'2312', u'port': u'80', u'condition': u'ENABLED', u'address': u'192.168.1.2'}] |
+--------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

Create a Shared Load Balancer
-----------------------------

It is possible for a single logical load balancer to balancer traffic for both
HTTP and HTTPS for a site.  For this example we will add an HTTPS load balancer
to the load balancer we created previously:

.. code-block:: bash

   libra_client --os_auth_url=https://company.com/openstack/auth/url \
   --os_username=username --os_password=pasword --os_tenant_name=tenant \
   --os_region_name=region create --name=my_load_balancer \
   --node 192.168.1.1:443 --node 192.168.1.2:443 --protocol=TCP --port=443 \
   --vip=52

We have taken the IP ID which was provided in the original create and given this
as a VIP number in the command.  We are also setting to TCP mode so the SSL
termination happens at the web server and set the load balancer to listen on
port 443.  The result is as follows:

+------+------------------+----------+------+-------------+--------+-------------------+-------------------+
|  ID  |       Name       | Protocol | Port |  Algorithm  | Status |      Created      |      Updated      |
+------+------------------+----------+------+-------------+--------+-------------------+-------------------+
| 1158 | my_load_balancer |   TCP    | 443  | ROUND_ROBIN | BUILD  | 2013-01-10T14:44Z | 2013-01-10T14:44Z |
+------+------------------+----------+------+-------------+--------+-------------------+-------------------+

+--------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                                            IPs                                             |                                                                                                             Nodes                                                                                                              |
+--------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| [{u'ipVersion': u'IPV_4', u'type': u'PUBLIC', u'id': u'52', u'address': u'15.185.224.62'}] | [{u'status': u'ONLINE', u'id': u'2313', u'port': u'443', u'condition': u'ENABLED', u'address': u'192.168.1.1'}, {u'status': u'ONLINE', u'id': u'2314', u'port': u'443', u'condition': u'ENABLED', u'address': u'192.168.1.2'}] |
+--------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

Add a Node
----------

.. code-block:: bash

   libra_client --os_auth_url=https://company.com/openstack/auth/url \
   --os_username=username --os_password=pasword --os_tenant_name=tenant \
   --os_region_name=region node-add --id=1158 --node=192.168.1.3:443

In this example we have take the ID of the load balancer of the previos example
to add a web server to.  The result should look something like this:

+----+-------------+------+-----------+--------+
| ID |   Address   | Port | Condition | Status |
+----+-------------+------+-----------+--------+
|    | 192.168.1.3 | 443  |           |        |
+----+-------------+------+-----------+--------+

