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
from libraclient.openstack.common.apiclient import client
from libraclient.openstack.common.apiclient import exceptions
from libraclient.v1_1.algorithms import AlgorithmManager
from libraclient.v1_1.loadbalancer import LoadBalancerManager
from libraclient.v1_1.limits import LimitManager
from libraclient.v1_1.protocols import ProtocolManager


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
    cls = exceptions._code_map.get(
        response.status_code, exceptions.ClientException
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
        return cls(http_status=response.status_code, message=message,
                   details=details, request_id=request_id, url=url,
                   method=method)
    else:
        return cls(request_id=request_id, url=url,
                   method=method)


exceptions.from_response = from_response


class Client(client.BaseClient):
    def __init__(self, *args, **kw):
        super(Client, self).__init__(*args, **kw)
        self.algorithms = AlgorithmManager(self)
        self.loadbalancers = LoadBalancerManager(self)
        self.limits = LimitManager(self)
        self.protocols = ProtocolManager(self)
