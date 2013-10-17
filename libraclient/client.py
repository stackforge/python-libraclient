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

from libraclient.openstack.common.apiclient import exceptions

import pkg_resources


def _find_versions():
    versions = {}
    for e in list(pkg_resources.iter_entry_points('libraclient.versions')):
        versions[e.name] = (e.module_name, e.load())
    return versions


def get_version(version):
    versions = _find_versions()
    try:
        return versions[version][1]
    except KeyError:
        raise exceptions.UnsupportedVersion('%s is not a supported version.' %
                                            version)


def VersionedClient(version, *args, **kw):
    cls = get_version(version)
    return cls(*args, **kw)
