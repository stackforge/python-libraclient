from libraclient.openstack.common.apiclient import base
from libraclient.v1_1.base import Manager


class Algorithm(base.Resource):
    def __repr__(self):
        return '<Algorithm: %s>' % self.name


class AlgorithmManager(Manager):
    resource_class = Algorithm

    def list(self):
        return self._list('/algorithms', 'algorithms')
