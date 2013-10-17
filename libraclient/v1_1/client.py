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

def from_response(response, method, url):
    """
    Return an instance of an ClientException or subclass
    based on an httplib2 response.

    Usage::

        resp, body = http.request(...)
        if resp.status != 200:
            raise exception_from_response(resp, body)
    """
    kwargs = {
        'http_status': response.status_code,
        'response': response,
        'method': method,
        'url': url,
    }
    if response.headers:
        kwargs['request_id'] = response.headers.get(
            'x-compute-request-id', None)
    if "retry-after" in response.headers:
        kwargs["retry_after"] = response.headers["retry-after"]

    if "retry-after" in response.headers:
        kwargs["retry_after"] = response.headers["retry-after"]

    content_type = response.headers.get("Content-Type", "")
    if content_type.startswith("application/json"):
        try:
            body = response.json()
        except ValueError:
            pass
        else:
            if isinstance(body, dict):
                kwargs['message'] = body.get('faultString', None) or \
                    body.get('message', None)
                kwargs["details"] = body.get("details", None)
    elif content_type.startswith("text/"):
        kwargs["details"] = response.text

    try:
        cls = exceptions._code_map[response.status_code]
    except KeyError:
        if 500 <= response.status_code < 600:
            cls = HttpServerError
        elif 400 <= response.status_code < 500:
            cls = HTTPClientError
        else:
            cls = HttpError
    return cls(**kwargs)


exceptions.from_response = from_response


class Client(client.BaseClient):
    def __init__(self, *args, **kw):
        super(Client, self).__init__(*args, **kw)
        self.algorithms = AlgorithmManager(self)
        self.loadbalancers = LoadBalancerManager(self)
        self.limits = LimitManager(self)
        self.protocols = ProtocolManager(self)
