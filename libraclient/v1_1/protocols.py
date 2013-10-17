# Copyright 2013 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from libraclient.openstack.common.apiclient import base
from libraclient.v1_1.base import Manager


class Protocol(base.Resource):
    def __repr__(self):
        return '<Protocol: %s>' % self.name


class ProtocolManager(Manager):
    resource_class = Protocol

    def list(self):
        return self._list('/protocols', 'protocols')
