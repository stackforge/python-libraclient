# Copyright 2012 Hewlett-Packard Development Company, L.P.
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

import prettytable
import novaclient
import socket
import logging

from novaclient import client


# NOTE(LinuxJedi): Override novaclient's error handler as we send messages in
# a slightly different format which causes novaclient's to throw an exception

def from_response(response, body, url, method=None):
    """
    Return an instance of an ClientException or subclass
    based on an httplib2 response.

    Usage::

        resp, body = http.request(...)
        if resp.status != 200:
            raise exception_from_response(resp, body)
    """
    cls = novaclient.exceptions._code_map.get(
        response.status_code, novaclient.exceptions.ClientException
    )
    if response.headers:
        request_id = response.headers.get('x-compute-request-id')
    else:
        request_id = None
    if body:
        message = "n/a"
        details = "n/a"
        if hasattr(body, 'keys'):
            message = body.get('faultstring', None)
            if not message:
                message = body.get('message', None)
            details = body.get('details', None)
        return cls(code=response.status_code, message=message, details=details,
                   request_id=request_id, url=url, method=method)
    else:
        return cls(code=response.status_code, request_id=request_id, url=url,
                   method=method)

novaclient.exceptions.from_response = from_response


class LibraAPI(object):
    def __init__(self, args):
        if args.debug:
            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG)

        self.nova = client.HTTPClient(
            args.os_username,
            args.os_password,
            args.os_tenant_name,
            args.os_auth_url,
            region_name=args.os_region_name,
            service_type=args.service_type,
            http_log_debug=args.debug,
            insecure=args.insecure,
            bypass_url=args.bypass_url
        )

    def limits_lb(self, args):
        resp, body = self._get('/limits')
        # Work around the fact that limits is missing from HP's API server
        if 'rate' in body['limits']:
            column_names = ['Verb', 'Value', 'Remaining', 'Unit',
                            'Next Available']
            columns = ['verb', 'value', 'remaining', 'unit', 'next-available']
            self._render_list(column_names, columns,
                              body['limits']['rate']['values']['limit'])
        column_names = ['Values']
        columns = ['values']
        self._render_dict(column_names, columns, body['limits']['absolute'])

    def protocols_lb(self, args):
        resp, body = self._get('/protocols')
        column_names = ['Name', 'Port']
        columns = ['name', 'port']
        self._render_list(column_names, columns, body['protocols'])

    def algorithms_lb(self, args):
        resp, body = self._get('/algorithms')
        column_names = ['Name']
        columns = ['name']
        self._render_list(column_names, columns, body['algorithms'])

    def list_lb(self, args):
        if args.deleted:
            resp, body = self._get('/loadbalancers?status=DELETED')
        else:
            resp, body = self._get('/loadbalancers')
        column_names = ['Name', 'ID', 'Protocol', 'Port', 'Algorithm',
                        'Status', 'Created', 'Updated', 'Node Count']
        columns = ['name', 'id', 'protocol', 'port', 'algorithm', 'status',
                   'created', 'updated', 'nodeCount']
        self._render_list(column_names, columns, body['loadBalancers'])

    def status_lb(self, args):
        resp, body = self._get('/loadbalancers/{0}'.format(args.id))
        column_names = ['ID', 'Name', 'Protocol', 'Port', 'Algorithm',
                        'Status', 'Status Description', 'Created', 'Updated',
                        'IPs', 'Nodes', 'Persistence Type',
                        'Connection Throttle', 'Node Count']
        columns = ['id', 'name', 'protocol', 'port', 'algorithm', 'status',
                   'statusDescription', 'created', 'updated', 'virtualIps',
                   'nodes', 'sessionPersistence', 'connectionThrottle',
                   'nodeCount']
        if 'sessionPersistence' not in body:
            body['sessionPersistence'] = 'None'
        if 'connectionThrottle' not in body:
            body['connectionThrottle'] = 'None'
        if 'statusDescription' in body:
            body['statusDescription'] = body['statusDescription'].rstrip()
        else:
            body['statusDescription'] = 'None'
        self._render_dict(column_names, columns, body)

    def virtualips_lb(self, args):
        resp, body = self._get('/loadbalancers/{0}/virtualips'.format(args.id))
        column_names = ['ID', 'Address', 'Type', 'IP Version']
        columns = ['id', 'address', 'type', 'ipVersion']
        self._render_list(column_names, columns, body['virtualIps'])

    def delete_lb(self, args):
        self._delete('/loadbalancers/{0}'.format(args.id))

    def create_lb(self, args):
        data = {}
        data['name'] = args.name
        if args.port is not None:
            data['port'] = args.port
        if args.protocol is not None:
            data['protocol'] = args.protocol
        if args.algorithm is not None:
            data['algorithm'] = args.algorithm
        data['nodes'] = self._parse_nodes(args.node)
        if args.vip is not None:
            data['virtualIps'] = [{'id': args.vip}]

        resp, body = self._post('/loadbalancers', body=data)
        column_names = ['ID', 'Name', 'Protocol', 'Port', 'Algorithm',
                        'Status', 'Created', 'Updated', 'IPs', 'Nodes']
        columns = ['id', 'name', 'protocol', 'port', 'algorithm', 'status',
                   'created', 'updated', 'virtualIps', 'nodes']
        self._render_dict(column_names, columns, body)

    def modify_lb(self, args):
        data = {}
        if args.name is not None:
            data['name'] = args.name
        if args.algorithm is not None:
            data['algorithm'] = args.algorithm
        self._put('/loadbalancers/{0}'.format(args.id), body=data)

    def node_list_lb(self, args):
        resp, body = self._get('/loadbalancers/{0}/nodes'.format(args.id))
        column_names = ['ID', 'Address', 'Port', 'Condition', 'Weight',
                        'Status']
        columns = ['id', 'address', 'port', 'condition', 'weight', 'status']
        self._render_list(column_names, columns, body['nodes'])

    def node_delete_lb(self, args):
        self._delete('/loadbalancers/{0}/nodes/{1}'
                     .format(args.id, args.nodeid))

    def node_add_lb(self, args):
        data = {}

        data['nodes'] = self._parse_nodes(args.node)
        resp, body = self._post('/loadbalancers/{0}/nodes'
                                .format(args.id), body=data)
        column_names = ['ID', 'Address', 'Port', 'Condition', 'Weight',
                        'Status']
        columns = ['id', 'address', 'port', 'condition', 'weight', 'status']
        self._render_list(column_names, columns, body['nodes'])

    def node_modify_lb(self, args):
        data = {'condition': args.condition, 'weight': args.weight}
        self._put('/loadbalancers/{0}/nodes/{1}'
                  .format(args.id, args.nodeid), body=data)

    def node_status_lb(self, args):
        resp, body = self._get('/loadbalancers/{0}/nodes/{1}'
                               .format(args.id, args.nodeid))
        column_names = ['ID', 'Address', 'Port', 'Condition',
                        'Weight', 'Status']
        columns = ['id', 'address', 'port', 'condition', 'weight', 'status']
        self._render_dict(column_names, columns, body)

    def logs_lb(self, args):
        data = {}

        if args.storage:
            data['objectStoreType'] = args.storage
        if args.endpoint:
            data['objectStoreEndpoint'] = args.endpoint
        if args.basepath:
            data['objectStoreBasePath'] = args.basepath
        if args.token:
            data['authToken'] = args.token

        resp, body = self._post('/loadbalancers/{0}/logs'.format(args.id),
                                body=data)

    def monitor_delete_lb(self, args):
        resp, body = self._delete('/loadbalancers/{0}/healthmonitor'
                                  .format(args.id))

    def monitor_list_lb(self, args):
        resp, body = self._get('/loadbalancers/{0}/healthmonitor'
                               .format(args.id))
        column_names = ['Type', 'Delay', 'Timeout', 'Attempts', 'Path']
        columns = ['type', 'delay', 'timeout', 'attemptsBeforeDeactivation',
                   'path']
        self._render_dict(column_names, columns, body or {})

    def monitor_modify_lb(self, args):
        data = {}
        data['type'] = args.type
        data['delay'] = args.delay
        data['timeout'] = args.timeout
        data['attemptsBeforeDeactivation'] = args.attempts
        if args.type.upper() != "CONNECT":
            data['path'] = args.path
        resp, body = self._put('/loadbalancers/{0}/healthmonitor'
                               .format(args.id), body=data)

    def _render_list(self, column_names, columns, data):
        table = prettytable.PrettyTable(column_names)
        for item in data:
            row = []
            for column in columns:
                if column in item:
                    rdata = item[column]
                else:
                    rdata = ''
                row.append(rdata)
            table.add_row(row)
        print table

    def _render_dict(self, column_names, columns, data):
        table = prettytable.PrettyTable(column_names)
        row = []
        for column in columns:
            if column in data:
                rdata = data[column]
            else:
                rdata = ''
            row.append(rdata)
        table.add_row(row)
        print table

    def _get(self, url, **kwargs):
        return self.nova.get(url, **kwargs)

    def _post(self, url, **kwargs):
        return self.nova.post(url, **kwargs)

    def _put(self, url, **kwargs):
        return self.nova.put(url, **kwargs)

    def _delete(self, url, **kwargs):
        return self.nova.delete(url, **kwargs)

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
