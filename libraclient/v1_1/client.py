from libraclient.openstack.common.apiclient.client import BaseClient
from libraclient.v1_1.loadbalancer import LBManager


class Client(BaseClient):
    def __init__(self, *args, **kw):
        super(Client, self).__init__(*args, **kw)
        self.lb = LBManager(self)
