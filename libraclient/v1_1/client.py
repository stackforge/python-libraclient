from libraclient.openstack.common.apiclient.client import (
    HTTPClient as BaseHTTPClient, BaseClient)
from libraclient.v1_1.loadbalancer import LBManager


class HTTPClient(BaseHTTPClient):
    def __init__(self, *args, **kw):
        print args
        self.kw = kw
    pass

class Client(BaseClient):
    def __init__(self, *args, **kw):
        http = HTTPClient(*args, **kw)
        #super(Client, self).__init__()
        #self.lb = LBManager(self)
