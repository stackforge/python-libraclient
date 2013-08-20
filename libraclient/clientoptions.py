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

import argparse
from novaclient import utils

LIBRA_DEFAULT_SERVICE_TYPE = 'hpext:lbaas'


class ClientOptions(object):
    def __init__(self):
        self.options = argparse.ArgumentParser('Libra command line client')

    def _generate(self):
        self.options.add_argument(
            '--os_auth_url',
            metavar='<auth-url>',
            default=utils.env('OS_AUTH_URL', 'LIBRA_URL'),
            help='Authentication URL'
        )
        self.options.add_argument(
            '--os_username',
            metavar='<auth-user-name>',
            default=utils.env('OS_USERNAME', 'LIBRA_USERNAME'),
            help='Authentication username'
        )
        self.options.add_argument(
            '--os_password',
            metavar='<auth-password>',
            default=utils.env('OS_PASSWORD', 'LIBRA_PASSWORD'),
            help='Authentication password'
        )
        self.options.add_argument(
            '--os_tenant_name',
            metavar='<auth-tenant-name>',
            default=utils.env('OS_TENANT_NAME', 'LIBRA_PROJECT_ID'),
            help='Authentication tenant'
        )
        self.options.add_argument(
            '--os_region_name',
            metavar='<region-name>',
            default=utils.env('OS_REGION_NAME', 'LIBRAL_REGION_NAME'),
            help='Authentication region'
        )
        self.options.add_argument(
            '--debug',
            action='store_true',
            help='Debug network messages'
        )
        self.options.add_argument(
            '--insecure',
            action='store_true',
            help='Don\'t verify SSL cert'
        )
        self.options.add_argument(
            '--bypass_url',
            help='Use this API endpoint instead of the Service Catalog'
        )
        self.options.add_argument(
            '--service_type',
            default=LIBRA_DEFAULT_SERVICE_TYPE,
            help='Default ' + LIBRA_DEFAULT_SERVICE_TYPE
        )

        subparsers = self.options.add_subparsers(
            metavar='<subcommand>', dest='command'
        )

        subparsers.add_parser(
            'algorithms', help='get a list of supported algorithms'
        )

        sp = subparsers.add_parser(
            'create', help='create a load balancer'
        )
        sp.add_argument('--name', help='name for the load balancer',
                        required=True)
        sp.add_argument('--port',
                        help='port for the load balancer, 80 is default')
        sp.add_argument('--protocol',
                        help='protocol for the load balancer, HTTP is default',
                        choices=['HTTP', 'TCP'])
        sp.add_argument('--algorithm',
                        help='algorithm for the load balancer,'
                             ' ROUND_ROBIN is default',
                        choices=['LEAST_CONNECTIONS', 'ROUND_ROBIN'])
        sp.add_argument('--node',
                        help='a node for the load balancer in ip:port format',
                        action='append', required=True)
        sp.add_argument('--vip',
                        help='the virtual IP to attach the load balancer to')

        sp = subparsers.add_parser(
            'delete', help='delete a load balancer'
        )
        sp.add_argument('--id', help='load balancer ID', required=True)

        subparsers.add_parser(
            'limits', help='get account API usage limits'
        )

        sp = subparsers.add_parser(
            'list', help='list load balancers'
        )
        sp.add_argument(
            '--deleted', help='list deleted load balancers',
            action='store_true'
        )

        sp = subparsers.add_parser(
            'logs', help='send a snapshot of logs to an object store'
        )
        sp.add_argument('--id', help='load balancer ID', required=True)
        sp.add_argument('--storage', help='storage type', choices=['Swift'])
        sp.add_argument('--endpoint', help='object store endpoint to use')
        sp.add_argument('--basepath', help='object store based directory')
        sp.add_argument('--token', help='object store authentication token')

        sp = subparsers.add_parser(
            'modify', help='modify a load balancer'
        )
        sp.add_argument('--id', help='load balancer ID', required=True)
        sp.add_argument('--name', help='new name for the load balancer')
        sp.add_argument('--algorithm',
                        help='new algorithm for the load balancer',
                        choices=['LEAST_CONNECTIONS', 'ROUND_ROBIN'])

        sp = subparsers.add_parser(
            'monitor-list',
            help='list health monitor information'
        )
        sp.add_argument('--id', required=True, help='load balancer ID')

        sp = subparsers.add_parser(
            'monitor-delete',
            help='delete a health monitor'
        )
        sp.add_argument('--id', required=True, help='load balancer ID')

        sp = subparsers.add_parser(
            'monitor-modify',
            help='modify a health monitor'
        )
        sp.add_argument('--id', required=True, help='load balancer ID')
        sp.add_argument('--type', choices=['CONNECT', 'HTTP'],
                        default='CONNECT', help='health monitor type')
        sp.add_argument('--delay', type=int, default=30, metavar='SECONDS',
                        help='time between health monitor calls')
        sp.add_argument('--timeout', type=int, default=30, metavar='SECONDS',
                        help='time to wait before monitor times out')
        sp.add_argument('--attempts', type=int, default=2, metavar='COUNT',
                        help='connection attempts before marking node as bad')
        sp.add_argument('--path',
                        help='URI path for health check')

        sp = subparsers.add_parser(
            'node-add', help='add node to a load balancer'
        )
        sp.add_argument('--id', help='load balancer ID', required=True)
        sp.add_argument('--node', help='node to add in ip:port form',
                        required=True, action='append')

        sp = subparsers.add_parser(
            'node-delete', help='delete node from a load balancer'
        )
        sp.add_argument('--id', help='load balancer ID', required=True)
        sp.add_argument('--nodeid',
                        help='node ID to remove from load balancer',
                        required=True)

        sp = subparsers.add_parser(
            'node-list', help='list nodes in a load balancer'
        )
        sp.add_argument('--id', help='load balancer ID', required=True)

        sp = subparsers.add_parser(
            'node-modify', help='modify node in a load balancer'
        )
        sp.add_argument('--id', help='load balancer ID', required=True)
        sp.add_argument('--nodeid', help='node ID to modify', required=True)
        sp.add_argument('--condition', help='the new state for the node',
                        choices=['ENABLED', 'DISABLED'], required=True)

        sp = subparsers.add_parser(
            'node-status', help='get status of a node in a load balancer'
        )
        sp.add_argument('--id', help='load balancer ID', required=True)
        sp.add_argument('--nodeid', help='node ID to get status from',
                        required=True)

        subparsers.add_parser(
            'protocols', help='get a list of supported protocols and ports'
        )

        sp = subparsers.add_parser(
            'status', help='get status of a load balancer'
        )
        sp.add_argument('--id', help='load balancer ID', required=True)

        sp = subparsers.add_parser(
            'virtualips', help='get a list of virtual IPs'
        )
        sp.add_argument('--id', help='load balancer ID', required=True)

    def run(self):
        self._generate()
        return self.options.parse_args()
