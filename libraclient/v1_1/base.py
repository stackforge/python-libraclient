from urllib import urlencode
from libraclient.openstack.common.apiclient.base import ManagerWithFind


class Manager(ManagerWithFind):
    def build_url(self, url, params):
        q = urlencode(params) if params else ''
        return '%(url)s%(params)s' % {
            'url': url,
            'params': '?%s' % q
        }