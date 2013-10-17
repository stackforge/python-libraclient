from libraclient.openstack.common.apiclient.base import getid, Resource
from libraclient.v1_1.base import Manager

import socket


class Node(Resource):
    def __repr__(self):
        return '<Node: %s' % self.manager.format_node(self._info)

class Monitor(Resource):
    def __repr__(self):
        return '<Monitor: %s>' % self.name


class LoadBalancer(Resource):
    def __repr__(self):
        return '<LoadBalancer: %s>' % self.name

    def delete(self):
        self.manager.delete(self)

    def update(self, **kw):
        self.manager.update(self, **kw)

    def list_vip(self):
        return self.manager.list_vip(self)

    def list_nodes(self):
        self.manager.list_nodes(self)


class LoadBalancerManager(Manager):
    resource_class = LoadBalancer

    @staticmethod
    def format_node(node):
        return '{status}/{condition} - {id} - {address}:{port}'.format(**node)

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
               virtual_ips=None):
        """
        Create a LoadBalancer from given values.
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
        if virtual_ips is not None:
            body['virtualIps'] = virtual_ips
        return self._post('/loadbalancers', body)

    def get(self, lb):
        """
        Get a LBM

        :param lb: The :class:`LoadBalancer` (or its ID) to update.
        """
        lb = self._get('/loadbalancers/%s' % getid(lb))
        return lb

    def list(self, deleted=False):
        """

        :param deleted: Show deleted LBs
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

        :param lb: The :class:`LoadBalancer` (or its ID) to update.
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

        :param lb: The :class:`LoadBalancer` (or its ID) to update.
        """
        self._delete('/loadbalancers/%s' % getid(lb))

    def create_node(self, lb, node):
        data = {}
        data['nodes'] = self._parse_nodes(node)
        return self._post('/loadbalancers/%s/nodes' % getid(lb),
                          data, obj_class=Node)

    def get_node(self, lb, node):
        url = '/loadbalancers/%s/nodes/%s' % (getid(lb), getid(node))
        return self._get(url, obj_class=Node)

    def list_nodes(self, lb):
        url = '/loadbalancers/%s/nodes' % getid(lb)
        return self._list(url, 'nodes', obj_class=Node)

    def update_node(self, lb, node, condition=None, weight=None):
        data = {}
        if condition is not None:
            data['condition'] = condition
        if weight is not None:
            data['weight'] = weight
        url = '/loadbalancers/%s/nodes/%s' % (getid(lb), getid(node))
        return self._put(url, data, obj_class=Node)

    def delete_node(self, lb, node):
        url = '/loadbalancers/%s/nodes/%s' % (getid(lb), getid(node))
        self._delete(url)

    def get_monitor(self, lb):
        url = '/loadbalancers/%s/healthmonitor' % getid(lb)
        return self._get(url, obj_class=Monitor)

    def update_monitor(self, lb, type_='CONNECT', delay=30, timeout=30,
                       attempts=2, path=None):
        data = {}
        data['type'] = type_
        data['delay'] = delay
        data['timeout'] = timeout
        data['attemptsBeforeDeactivation'] = attempts

        if type_.upper() != 'CONNECT':
            data['path'] = path

        url = '/loadbalancers/%s/healthmonitor' % getid(lb)
        return self._put(url, data, obj_class=Monitor)

    def delete_monitor(self, lb):
        url = '/loadbalancers/%s/healthmonitor' % getid(lb)
        self._delete(url)

    def list_vip(self, lb):
        """
        List Virtual IPs for a LoadBalancer

        :param lb: The :class:`LoadBalancer` (or its ID) to update.
        """
        res = self.client.get('loadbalancers/%s/virtualips' % getid(lb))
        return res.json()['virtualIps']
