# Copyright 2013 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from libraclient.openstack.common.apiclient.base import getid, Resource
from libraclient.v1_1.base import Manager

import socket


class Node(Resource):
    def __repr__(self):
        s = '<Node: {address}:{port}>'
        return s.format(**self._info)


class Monitor(Resource):
    def __repr__(self):
        return '<Monitor: %s>' % self.name


class VirtualIP(Resource):
    def __repr__(self):
        s = '<VIP: {id} - {type} {ipVersion} {address}>'
        return s.format(**self._info)


class LoadBalancer(Resource):
    def __init__(self, manager, info, loaded=False):
        info['nodes'] = [Node(self, n) for n in info.pop('nodes', [])]
        info['virtualIps'] = [VirtualIP(self, n)
                              for n in info.pop('virtualIps', [])]
        super(LoadBalancer, self).__init__(manager, info, loaded=False)

    def __repr__(self):
        return '<LoadBalancer: %s>' % self.name

    def delete(self):
        self.manager.delete(self)

    def update(self, **kw):
        self.manager.update(self, **kw)

    def create_node(self, node):
        return self.manager.create_node(node)

    def list_nodes(self):
        return self.manager.list_nodes(self)

    def get_node(self, node):
        return self.manager.get_node(self, node)

    def update_node(self, node, condition=None, weight=None):
        return self.manager.update_node(self, node,
                                        condition=condition, weight=weight)

    def delete_node(self, node):
        return self.manager.delete_node(self, node)

    def update_monitor(self, type_='CONNECT', delay=30, timeout=30,
                       attempts=2, path=None):
        return self.manager.update_monitor(
            self, type_=type_, delay=delay, timeout=timeout, attempts=attempts,
            path=path)

    def delete_monitor(self, lb):
        self.manager.delete_monitor(lb)

    def list_vip(self):
        return self.manager.list_vip(self)


class LoadBalancerManager(Manager):
    resource_class = LoadBalancer

    def _parse_nodes(self, nodes):
        out_nodes = []
        try:
            for node in nodes:
                nodeopts = node.split(':')
                ipaddr = nodeopts[0]
                port = nodeopts[1]
                weight, backup = None, None

                # Test IP valid
                # TODO: change to pton when we want to support IPv6
                socket.inet_aton(ipaddr)
                # Test port valid
                if int(port) < 0 or int(port) > 65535:
                    raise Exception('Port out of range')

                # Process the rest of the node options as key=value
                for kv in nodeopts[2:]:
                    key, value = kv.split('=')
                    key = key.lower()
                    value = value.upper()
                    if key == 'weight':
                        weight = int(value)
                    elif key == 'backup':
                        backup = value    # 'TRUE' or 'FALSE'
                    else:
                        raise Exception("Unknown node option '%s'" % key)

                node_def = {'address': ipaddr, 'port': port}
                if weight:
                    node_def['weight'] = weight
                if backup:
                    node_def['backup'] = backup

                out_nodes.append(node_def)
        except Exception as e:
            raise Exception("Invalid value specified for --node: %s" % e)
        return out_nodes

    def create(self, name, nodes, port=None, protocol=None, algorithm=None,
               virtual_ip=None):
        """
        Create a LoadBalancer from given values.

        :param name: The name / display name.
        :param nodes: Nodes.
        :param port: Numeric port (80, 443 for example.)
        :param protocol: Protocol to use (TCP / HTTP for example.)
        :param algorithm: Algorithm (ROUND_ROBIN for example.)
        :param virtual_ip: VIP ID to set if Shared LB.
        """
        parsed_nodes = self._parse_nodes(nodes)
        body = {
            'name': name,
            'nodes': parsed_nodes,
        }
        if port is not None:
            body['port'] = port
        if protocol is not None:
            body['protocol'] = protocol
        if algorithm is not None:
            body['algorithm'] = algorithm
        if virtual_ip is not None:
            body['virtualIps'] = [{'id': virtual_ip}]
        return self._post('/loadbalancers', body)

    def get(self, lb):
        """
        Get a LoadBalancer.

        :param lb: The :class:`LoadBalancer` (or its ID) to update.
        """
        lb = self._get('/loadbalancers/%s' % getid(lb))
        return lb

    def list(self, deleted=False):
        """
        List loadBalancers.

        :param deleted: Show deleted LoadBalancers.
        """
        params = {}
        if deleted:
            params['status'] = 'DELETED'

        url = self.build_url('/loadbalancers', params)
        lbs = self._list(url, 'loadBalancers')
        return lbs

    def update(self, lb, name=None, algorithm=None):
        """
        Update a LoadBalancer

        :param lb: The :class:`LoadBalancer` (or its ID).
        :param name: Set the name of the LoadBalancer.
        :param algorithm: Algorithm (ROUND_ROBIN for example.)
        """
        data = {}
        if name is not None:
            data['name'] = name
        if algorithm is not None:
            data['algorithm'] = algorithm
        return self._put('/loadbalancers/%s' % getid(lb), data)

    def delete(self, lb):
        """
        Delete a LoadBalancer

        :param lb: The :class:`LoadBalancer` (or its ID).
        """
        self._delete('/loadbalancers/%s' % getid(lb))

    def create_node(self, lb, node):
        data = {}
        data['nodes'] = self._parse_nodes(node)

        url = '/loadbalancers/%s/nodes' % getid(lb)
        nodes = self._post(url, data, return_raw=True, response_key='nodes')
        return [Node(self, n) for n in nodes]

    def get_node(self, lb, node):
        """
        Get a Node belonging to a LoadBalancer

        :param lb: The :class:`LoadBalancer` (or its ID).
        :param node: The :class:`Node` (or its ID).
        """
        url = '/loadbalancers/%s/nodes/%s' % (getid(lb), getid(node))
        return self._get(url, obj_class=Node)

    def list_nodes(self, lb):
        """
        List Nodes belonging to a LoadBalancer.

        :param lb: The :class:`LoadBalancer` (or its ID)..
        """
        url = '/loadbalancers/%s/nodes' % getid(lb)
        return self._list(url, 'nodes', obj_class=Node)

    def update_node(self, lb, node, condition=None, weight=None):
        """
        Update a node

        :param lb: The :class:`LoadBalancer` (or its ID).
        :param node: The :class:`Node` (or its ID).
        :param condition: Set the conditioon.
        :param weight: Set the weight.
        """
        data = {}
        if condition is not None:
            data['condition'] = condition
        if weight is not None:
            data['weight'] = weight
        url = '/loadbalancers/%s/nodes/%s' % (getid(lb), getid(node))
        return self._put(url, data, obj_class=Node)

    def delete_node(self, lb, node):
        """
        Delete a node from a LoadBalancer.

        :param lb: The :class:`LoadBalancer` (or its ID).
        :param node: The :class:`Node` (or its ID).
        """
        url = '/loadbalancers/%s/nodes/%s' % (getid(lb), getid(node))
        self._delete(url)

    def get_monitor(self, lb):
        """
        Get a Monitor for a LoadBalancer

        :param lb: The :class:`LoadBalancer` (or its ID).
        """
        url = '/loadbalancers/%s/healthmonitor' % getid(lb)
        return self._get(url, obj_class=Monitor)

    def update_monitor(self, lb, type_='CONNECT', delay=30, timeout=30,
                       attempts=2, path=None):
        """
        Update a Monitor in a LoadBalancer

        :param lb: The :class:`LoadBalancer` (or its ID).
        :param type_: Monitor type.
        :param delay: Numeric delay, must be less then timeout.
        :param timeout: Numeric timeout, must be geater then delay.
        :param attempts: Max attempts before deactivation.
        :param path: URI path when using HTTP type.
        """
        data = {}
        data['type'] = type_
        if timeout > delay:
            raise ValueError('Timeout can\'t be greater then Delay')
        data['delay'] = delay
        data['timeout'] = timeout
        data['attemptsBeforeDeactivation'] = attempts

        if type_.upper() != 'CONNECT':
            data['path'] = path

        url = '/loadbalancers/%s/healthmonitor' % getid(lb)
        return self._put(url, data, obj_class=Monitor)

    def delete_monitor(self, lb):
        """
        Delete monitor from a LoadBalancer

        :param lb: The :class:`LoadBalancer` (or its ID).
        """
        url = '/loadbalancers/%s/healthmonitor' % getid(lb)
        self._delete(url)

    def list_vip(self, lb):
        """
        List Virtual IPs for a LoadBalancer

        :param lb: The :class:`LoadBalancer` (or its ID) to update.
        """
        return self._list('loadbalancers/%s/virtualips' % getid(lb),
                          response_key='virtualIps', obj_class=VirtualIP)

    def send_logs(self, lb, values):
        """
        Send a snapshot of logs somewhere.

        :param lb: The :class:`LoadBalancer` (or its ID).
        :param storage: Storage type.
        :param kw: The values to send it with, pass as kw.
        """
        self.client.post('/loadbalancers/%s/logs' % getid(lb), json=values)
