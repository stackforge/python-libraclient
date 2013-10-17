from urllib import urlencode
from libraclient.openstack.common.apiclient import base
from libraclient.v1_1.base import Manager


class LoadBalancer(base.Resource):
    def __repr__(self):
        return '<LoadBalancer: %s>' % self.name

    def delete(self):
        self.manager.delete(self)

    def update(self, **kw):
        self.manager.update(self, **kw)


class LBManager(Manager):
    resource_class = LoadBalancer

    def create(self):
        pass

    def get(self, lb):
        """
        Get a LBM

        :param lb: The :class:`LoadBalancer` (or its ID) to update.
        """
        lb = self._get('/loadbalancers/%s' % base.getid(lb), None)
        return lb

    def list(self, deleted=False):
        """
        :param deleted: Show deleted LBs
        """
        params = {}
        if deleted:
            params['status'] = 'DELETED'

        url = self.build_url('/loadbalancers', params)
        lbs = self._list(url, 'loadBalancers')
        return lbs

    def update(self, lb, **kw):
        """
        :param lb: The :class:`LoadBalancer` (or its ID) to update.
        """
        self._put('/loadbalancers/%s' % base.getid(lb), kw, None)

    def delete(self, lb):
        self._delete('/loadbalancers/%s' % base.getid(lb))