# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import abc
import logging

from libraclient.openstack.common.apiclient import auth
from libraclient.openstack.common.apiclient import exceptions

from keystoneclient import access


logger = logging.getLogger(__name__)


class KeystoneBaseAuthPlugin(auth.BaseAuthPlugin):
    access_info = None

    def _endpoint(self, url=None):
        bypass_url = self.opts.get('bypass_url', '')
        if bypass_url:
            url = bypass_url
        return url

    def _do_authenticate(self, http_client):
        resp = self._get_auth_response(http_client)
        try:
            body = resp.json()
        except ValueError as ex:
            raise exceptions.AuthorizationFailure(ex)
        self.access_info = access.AccessInfo.factory(
            resp, body, region_name=http_client.region_name)



class KeystoneAuthPluginV2(KeystoneBaseAuthPlugin):
    auth_system = "keystone2"
    opt_names = [
        "auth_url",
        "user_id",
        "username",
        "password",
        "token",
        "tenant_id",
        "tenant_name",
        'bypass_url'
    ]

    def sufficient_options(self):
        have_identity = (
            self.opts.get("token") or
            (self.opts.get("username") and self.opts.get("password")))
        if not (self.opts.get("auth_url") and have_identity):
            req_opts = ("auth_url", "username", "password", "token")
            raise exceptions.AuthPluginOptionsMissing(
                [opt for opt in req_opts if not self.opts.get(opt)])

    def _get_auth_response(self, http_client):
        headers = {}
        token = self.opts.get("token")
        if token:
            params = {"auth": {"token": {"id": token}}}
            headers["X-Auth-Token"] = token
        else:
            params = {
                "auth": {
                    "passwordCredentials": {
                        "username": self.opts.get("username"),
                        "password": self.opts.get("password"),
                    }
                }
            }
        if self.opts.get("tenant_id"):
            params["auth"]["tenantId"] = self.opts.get("tenant_id")
        elif self.opts.get("tenant_name"):
            params["auth"]["tenantName"] = self.opts.get("tenant_name")
        return http_client.request(
            "POST",
            http_client.concat_url(self.opts.get("auth_url"), "/tokens"),
            allow_redirects=True,
            headers=headers,
            json=params)

    def token_and_endpoint(self, endpoint_type, service_type):
        if self.opts['token'] and self.opts['bypass_url']:
            return self.opts['token'], self.opts['bypass_url']
        url = self.access_info.service_catalog.url_for(
            service_type=service_type,
            endpoint_type=endpoint_type)
        return self.access_info.auth_token, self._endpoint(url)


class KeystoneAuthPluginV3(KeystoneBaseAuthPlugin):
    auth_system = "keystone3"
    opt_names = [
        "auth_url",
        "user_id",
        "username",
        "user_domain_id",
        "user_domain_name",
        "password",
        "domain_id",
        "domain_name",
        "project_id",
        "project_name",
        "project_domain_id",
        "project_domain_name",
        "token",
        "bypass_url"
    ]

    def sufficient_options(self):
        have_identity = (
            self.opts.get("token") or
            ((self.opts.get("username") or self.opts.get("user_id"))
             and self.opts.get("password")))
        if not (self.opts.get("auth_url") and have_identity):
            req_opts = ("auth_url", "username", "user_id", "password", "token")
            raise exceptions.AuthPluginOptionsMissing(
                [opt for opt in req_opts if not self.opts.get(opt)])

    def _set_id_or_name(self, dct, key, id_key, name_key):
        value = self.opts.get(id_key)
        if value:
            dct[key] = {"id": value}
            return
        value = self.opts.get(name_key)
        if value:
            dct[key] = {"name": value}

    def _get_auth_response(self, http_client):
        domain_scoped = (self.opts.get("domain_id") or
                         self.opts.get("domain_name"))
        project_scoped = (self.opts.get("project_id") or
                          self.opts.get("project_name"))

        if domain_scoped and project_scoped:
            raise ValueError("Authentication cannot be scoped to both domain"
                             " and project.")
        headers = {}
        body = {"auth": {"identity": {}}}
        ident = body["auth"]["identity"]

        token = self.opts.get("token")
        if token:
            headers["X-Auth-Token"] = token

            ident["methods"] = ["token"]
            ident["token"] = {}
            ident["token"]["id"] = token
        else:
            # password authentication
            ident["methods"] = ["password"]
            ident["password"] = {}
            self._set_id_or_name(ident["password"], "user",
                                 "user_id", "username")
            user = ident["password"]["user"]
            user["password"] = self.opts.get("password")

            if "name" in user:
                self._set_id_or_name(user, "domain",
                                     "user_domain_id", "user_domain_name")

        if domain_scoped or project_scoped:
            body["auth"]["scope"] = {}
            scope = body["auth"]["scope"]
            self._set_id_or_name(scope, "domain", "domain_id", "domain_name")
            if "domain" not in scope:
                # use project_id or project_name
                self._set_id_or_name(scope, "project",
                                     "project_id", "project_name")
                if "name" in scope["project"]:
                    self._set_id_or_name(
                        scope["project"], "domain",
                        "project_domain_id", "project_domain_name")

        return http_client.request(
            "POST",
            http_client.concat_url(self.opts.get("auth_url"), "/auth/tokens"),
            allow_redirects=True,
            headers=headers,
            json=body)

    def token_and_endpoint(self, endpoint_type, service_type):
        url = self.access_info.service_catalog.url_for(
            service_type=service_type,
            endpoint_type=endpoint_type)
        return self.access_info.auth_token, self._endpoint(url)
