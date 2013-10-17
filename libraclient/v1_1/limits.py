from libraclient.openstack.common.apiclient import base
from libraclient.v1_1.base import Manager


class Limit(base.Resource):
    def __repr__(self):
        return '<Limit: %s>' % self.name


class LimitManager(base.BaseManager):
    resource_class = Limit

    def list_limits(self):
        limits = []
        json = self.client.get('/limits').json()
        for lname, lvalues in json['limits'].items():
            values = lvalues['values']
            values['name'] = lname
            limits.append(Limit(self, values))
        return limits
