from libraclient.openstack.common.apiclient import base
from libraclient.v1_1.base import Manager


class Protocol(base.Resource):
    def __repr__(self):
        return '<Limit: %s>' % self.name


class ProtocolManager(Manager):
    resource_class = Protocol

    def list(self):
        return self._list('/protocols', 'protocols')