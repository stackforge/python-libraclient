from libraclient.openstack.common.apiclient import base
from libraclient.v1_1.base import Manager


class LoadBalancer(base.Resource):
    def __repr__(self):
        return '<LoadBalancer: %s>' % self.name

    def delete(self):
        self.manager.delete(self)

    def update(self, **kw):
        self.manager.update(self, **kw)

    def list_vip(self):
        return self.manager.list_vip(self)


class LoadBalancerManager(Manager):
    resource_class = LoadBalancer

    def create(self):
        """
        Create a LoadBalancer from given values.
        """
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
        Update a LoadBalancer

        :param lb: The :class:`LoadBalancer` (or its ID) to update.
        """
        self._put('/loadbalancers/%s' % base.getid(lb), kw, None)

    def delete(self, lb):
        """
        Delete a LoadBalancer

        :param lb: The :class:`LoadBalancer` (or its ID) to update.
        """
        self._delete('/loadbalancers/%s' % base.getid(lb))

    def list_vip(self, lb):
        """
        List Virtual IPs for a LoadBalancer

        :param lb: The :class:`LoadBalancer` (or its ID) to update.
        """
        return self._list('loadbalancers/%s/virtualips' %  base.getid(lb), 'virtualIps')