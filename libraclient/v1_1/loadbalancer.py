from libraclient.openstack.common.apiclient.base import (
    ManagerWithFind, Resource)


class LoadBalancer(Resource):
    pass


class LBManager(ManagerWithFind):
    def list(self):
        return self._list('/loadbalancers', 'loadBalancers')
