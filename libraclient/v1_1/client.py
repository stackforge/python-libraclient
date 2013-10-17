from libraclient.openstack.common.apiclient.client import BaseClient
from libraclient.v1_1.algorithms import AlgorithmManager
from libraclient.v1_1.loadbalancer import LoadBalancerManager
from libraclient.v1_1.limits import LimitManager
from libraclient.v1_1.protocols import ProtocolManager


class Client(BaseClient):
    def __init__(self, *args, **kw):
        super(Client, self).__init__(*args, **kw)
        self.algorithms = AlgorithmManager(self)
        self.loadbalancers = LoadBalancerManager(self)
        self.limits = LimitManager(self)
        self.protocols = ProtocolManager(self)
