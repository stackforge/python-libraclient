# Copyright 2012 Hewlett-Packard Development Company, L.P.
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

import sys
import os
from libraapi import LibraAPI
from clientoptions import ClientOptions
from libraclient.openstack.common.apiclient import exceptions

import pkg_resources


def main():
    options = ClientOptions()
    args = options.run()

    required_args = [
        'os_auth_url', 'os_username', 'os_password', 'os_tenant_name',
        'os_region_name'
    ]
    missing_args = 0
    for req in required_args:
        test_var = getattr(args, req)
        if test_var == '':
            missing_args += 1
            sys.stderr.write(
                '{app}: error: argument --{test_var} is required\n'
                .format(app=os.path.basename(sys.argv[0]), test_var=req))
    if missing_args:
        return 2

    api = LibraAPI(args)

    cmd = args.command.replace('-', '_')
    method = getattr(api, '{cmd}_lb'.format(cmd=cmd))

    try:
        method(args)
    except exceptions.ClientException as exc:
        print exc
        if exc.details:
            print exc.details
    except exceptions.EndpointNotFound:
        return 2
    except Exception as exc:
        print exc
        return 2

    return 0


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
        raise exceptions.UnsupportedVersion('%s is not a supported version.' % version)


def VersionedClient(version, *args, **kw):
    cls = get_version(version)
    return cls(*args, **kw)