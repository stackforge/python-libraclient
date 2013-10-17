from libraclient.openstack.common.apiclient import base
from libraclient.v1_1.base import Manager

import socket


class LoadBalancer(base.Resource):
    def __repr__(self):
        return '<LoadBalancer: %s>' % self.name

    def delete(self):
        self.manager.delete(self)

    def update(self, **kw):
        self.manager.update(self, **kw)

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
        self._post('/loadbalancers', body)

    def get(self, lb):
        """
        Get a LBM

        :param lb: The :class:`LoadBalancer` (or its ID) to update.
        """
        lb = self._get('/loadbalancers/%s' % base.getid(lb), None)
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
        self._put('/loadbalancers/%s' % base.getid(lb), data)

    def delete(self, lb):
        """
        Delete a LoadBalancer

        :param lb: The :class:`LoadBalancer` (or its ID) to update.
        """
        self._delete('/loadbalancers/%s' % base.getid(lb))

    def list_vip(self, lb):
        """
        List Virtual IPs for a LoadBalancer

        :param lb: The :class:`LoadBalancer` (or its ID) to update.
        """
        res = self.client.get('loadbalancers/%s/virtualips' % base.getid(lb))
        return res.json()['virtualIps']
