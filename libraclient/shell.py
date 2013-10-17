# Copyright 2010 Jacob Kaplan-Moss
# Copyright 2011 OpenStack Foundation
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
#
# NOTE: Partially copied from python-novaclient
"""
CLI (Command Line Interface) for Libra LBaaS tools
"""

from __future__ import print_function

import argparse
import getpass
import glob
import imp
import itertools
import os
import pkgutil
import sys
import logging

import pkg_resources
import six

HAS_KEYRING = False
all_errors = ValueError
try:
    import keyring
    HAS_KEYRING = True
    try:
        if isinstance(keyring.get_keyring(), keyring.backend.GnomeKeyring):
            import gnomekeyring
            all_errors = (ValueError,
                          gnomekeyring.IOError,
                          gnomekeyring.NoKeyringDaemonError)
    except Exception:
        pass
except ImportError:
    pass

import libraclient
from libraclient.client import VersionedClient
from libraclient.openstack.common.apiclient import auth
from libraclient.openstack.common.apiclient import base
from libraclient.openstack.common.apiclient import client
from libraclient.openstack.common.apiclient import exceptions as exc
from libraclient.openstack.common import cliutils
from libraclient.openstack.common import strutils
from libraclient.v1_1 import shell as shell_v1


DEFAULT_API_VERSION = "1.1"
DEFAULT_ENDPOINT_TYPE = 'publicURL'
DEFAULT_SERVICE_TYPE = 'hpext:lbaas'
DEFAULT_SERVICE_NAME = 'libra'

logger = logging.getLogger(__name__)


def positive_non_zero_float(text):
    if text is None:
        return None
    try:
        value = float(text)
    except ValueError:
        msg = "%s must be a float" % text
        raise argparse.ArgumentTypeError(msg)
    if value <= 0:
        msg = "%s must be greater than 0" % text
        raise argparse.ArgumentTypeError(msg)
    return value


class SecretsHelper(object):
    def __init__(self, args, client):
        self.args = args
        self.client = client
        self.key = None

    def _validate_string(self, text):
        if text is None or len(text) == 0:
            return False
        return True

    def _make_key(self):
        if self.key is not None:
            return self.key
        keys = [
            self.client.auth_plugin.opts['auth_url'],
            self.client.auth_plugin.opts['tenant_id'],
            self.client.auth_plugin.opts['username'],
            self.args.os_region_name,
            self.args.endpoint_type,
            self.args.service_type,
            self.args.service_name,
        ]
        for (index, key) in enumerate(keys):
            if key is None:
                keys[index] = '?'
            else:
                keys[index] = str(keys[index])
        self.key = "/".join(keys)
        return self.key

    def _prompt_password(self, verify=True):
        pw = None
        if hasattr(sys.stdin, 'isatty') and sys.stdin.isatty():
            # Check for Ctl-D
            try:
                while True:
                    pw1 = getpass.getpass('OS Password: ')
                    if verify:
                        pw2 = getpass.getpass('Please verify: ')
                    else:
                        pw2 = pw1
                    if pw1 == pw2 and self._validate_string(pw1):
                        pw = pw1
                        break
            except EOFError:
                pass
        return pw

    def save(self, client):
        if not HAS_KEYRING or not self.args.os_cache:
            return
        self.client = client
        auth_token, endpoint = client.auth_plugin.token_and_endpoint(
            self.args.endpoint_type, self.args.service_type)
        tenant_id = client.auth_plugin.access_info.tenant_id
        if (auth_token == self.auth_token and
                endpoint == self.endpoint):
            # Nothing changed....
            return
        if not all([endpoint, auth_token, tenant_id]):
            raise ValueError("Unable to save empty management url/auth token")
        value = "|".join([str(auth_token),
                          str(endpoint),
                          str(tenant_id)])
        keyring.set_password("libraclient_auth", self._make_key(), value)

    @property
    def password(self):
        if self._validate_string(self.args.os_password):
            return self.args.os_password
        verify_pass = strutils.bool_from_string(
            cliutils.env("OS_VERIFY_PASSWORD"))
        return self._prompt_password(verify_pass)

    @property
    def endpoint(self):
        if not HAS_KEYRING or not self.args.os_cache:
            return None
        url = None
        try:
            block = keyring.get_password('libraclient_auth', self._make_key())
            if block:
                _token, url, _tenant_id = block.split('|', 2)
        except all_errors:
            pass
        return url

    @property
    def auth_token(self):
        # Now is where it gets complicated since we
        # want to look into the keyring module, if it
        # exists and see if anything was provided in that
        # file that we can use.
        if not HAS_KEYRING or not self.args.os_cache:
            return None
        token = None
        try:
            block = keyring.get_password('libraclient_auth', self._make_key())
            if block:
                token, _endpoint, _tenant_id = block.split('|', 2)
        except all_errors:
            pass
        return token

    @property
    def tenant_id(self):
        if not HAS_KEYRING or not self.args.os_cache:
            return None
        tenant_id = None
        try:
            block = keyring.get_password('libraclient_auth', self._make_key())
            if block:
                _token, _endpoint, tenant_id = block.split('|', 2)
        except all_errors:
            pass
        return tenant_id


class LibraClientArgumentParser(argparse.ArgumentParser):

    def __init__(self, *args, **kwargs):
        super(LibraClientArgumentParser, self).__init__(*args, **kwargs)

    def error(self, message):
        """error(message: string)

        Prints a usage message incorporating the message to stderr and
        exits.
        """
        self.print_usage(sys.stderr)
        #FIXME(lzyeval): if changes occur in argparse.ArgParser._check_value
        choose_from = ' (choose from'
        progparts = self.prog.partition(' ')
        self.exit(2, "error: %(errmsg)s\nTry '%(mainp)s help %(subp)s'"
                     " for more information.\n" %
                     {'errmsg': message.split(choose_from)[0],
                      'mainp': progparts[0],
                      'subp': progparts[2]})


# I'm picky about my shell help.
class OpenStackHelpFormatter(argparse.HelpFormatter):
    def start_section(self, heading):
        # Title-case the headings
        heading = '%s%s' % (heading[0].upper(), heading[1:])
        super(OpenStackHelpFormatter, self).start_section(heading)


class LibraShell(object):
    def get_base_parser(self):
        parser = LibraClientArgumentParser(
            prog='libra',
            description=__doc__.strip(),
            epilog='See "libraclient help COMMAND" '
                   'for help on a specific command.',
            add_help=False,
            formatter_class=OpenStackHelpFormatter,
        )

        # Global arguments
        parser.add_argument(
            '-h', '--help',
            action='store_true',
            help=argparse.SUPPRESS,
        )

        parser.add_argument(
            '--version',
            action='version',
            version=libraclient.__version__)

        parser.add_argument(
            '--debug',
            default=False,
            action='store_true',
            help="Print debugging output")

        parser.add_argument(
            '--no-cache',
            default=not strutils.bool_from_string(
                cliutils.env('OS_NO_CACHE', default='true')),
            action='store_false',
            dest='os_cache',
            help=argparse.SUPPRESS)
        parser.add_argument(
            '--no_cache',
            action='store_false',
            dest='os_cache',
            help=argparse.SUPPRESS)

        parser.add_argument(
            '--os-cache',
            default=cliutils.env('OS_CACHE', default=False),
            action='store_true',
            help="Use the auth token cache.")

        parser.add_argument(
            '--timings',
            default=False,
            action='store_true',
            help="Print call timing info")

        parser.add_argument(
            '--api-timeout',
            default=600,
            metavar='<seconds>',
            type=positive_non_zero_float,
            help="Set HTTP call timeout (in seconds)")

        parser.add_argument(
            '--os-tenant-id',
            metavar='<auth-tenant-id>',
            default=cliutils.env('OS_TENANT_ID'),
            help='Defaults to env[OS_TENANT_ID].')

        parser.add_argument(
            '--os-region-name',
            metavar='<region-name>',
            default=cliutils.env('OS_REGION_NAME', 'LIBRA_REGION_NAME'),
            help='Defaults to env[OS_REGION_NAME].')
        parser.add_argument(
            '--os_region_name',
            help=argparse.SUPPRESS)

        parser.add_argument(
            '--service-type',
            metavar='<service-type>',
            default=cliutils.env('LIBRA_SERVICE_TYPE',
                                 default=DEFAULT_SERVICE_TYPE),
            help='Defaults to libra for most actions')
        parser.add_argument(
            '--service_type',
            help=argparse.SUPPRESS)

        parser.add_argument(
            '--service-name',
            metavar='<service-name>',
            default=cliutils.env('LIBRA_SERVICE_NAME',
                                 default=DEFAULT_SERVICE_NAME),
            help='Defaults to env[LIBRA_SERVICE_NAME]')
        parser.add_argument(
            '--service_name',
            help=argparse.SUPPRESS)

        parser.add_argument(
            '--endpoint-type',
            metavar='<endpoint-type>',
            default=cliutils.env('LIBRA_ENDPOINT_TYPE',
                                 default=DEFAULT_ENDPOINT_TYPE),
            help='Defaults to env[LIBRA_ENDPOINT_TYPE] or '
                    + DEFAULT_ENDPOINT_TYPE + '.')

        parser.add_argument(
            '--libra-api-version',
            metavar='<compute-api-ver>',
            default=cliutils.env('LIBRA_API_VERSION',
                                 default=DEFAULT_API_VERSION),
            help='Accepts 1.1'
                 'defaults to env[LIBRA_API_VERSION].')
        parser.add_argument(
            '--os_compute_api_version',
            help=argparse.SUPPRESS)

        parser.add_argument(
            '--os-cacert',
            metavar='<ca-certificate>',
            default=cliutils.env('OS_CACERT', default=None),
            help='Specify a CA bundle file to use in '
                 'verifying a TLS (https) server certificate. '
                 'Defaults to env[OS_CACERT]')

        parser.add_argument(
            '--insecure',
            default=cliutils.env('LIBRA_INSECURE', default=False),
            action='store_true',
            help="Explicitly allow libraclient to perform \"insecure\" "
                 "SSL (https) requests. The server's certificate will "
                 "not be verified against any certificate authorities. "
                 "This option should be used with caution.")

        # The auth-system-plugins might require some extra options
        auth.load_auth_system_opts(parser)

        return parser

    def get_subcommand_parser(self, version):
        parser = self.get_base_parser()

        self.subcommands = {}
        subparsers = parser.add_subparsers(metavar='<subcommand>')

        actions_module = shell_v1

        self._find_actions(subparsers, actions_module)
        self._find_actions(subparsers, self)

        for extension in self.extensions:
            self._find_actions(subparsers, extension.module)

        self._add_bash_completion_subparser(subparsers)

        return parser

    def _discover_extensions(self, version):
        extensions = []
        for name, module in itertools.chain(
                self._discover_via_python_path(),
                self._discover_via_contrib_path(version),
                self._discover_via_entry_points()):

            extension = base.Extension(name, module)
            extensions.append(extension)

        return extensions

    def _discover_via_python_path(self):
        for (module_loader, name, _ispkg) in pkgutil.iter_modules():
            if name.endswith('_python_libraclient_ext'):
                if not hasattr(module_loader, 'load_module'):
                    # Python 2.6 compat: actually get an ImpImporter obj
                    module_loader = module_loader.find_module(name)

                module = module_loader.load_module(name)
                if hasattr(module, 'extension_name'):
                    name = module.extension_name

                yield name, module

    def _discover_via_contrib_path(self, version):
        module_path = os.path.dirname(os.path.abspath(__file__))
        version_str = "v%s" % version.replace('.', '_')
        ext_path = os.path.join(module_path, version_str, 'contrib')
        ext_glob = os.path.join(ext_path, "*.py")

        for ext_path in glob.iglob(ext_glob):
            name = os.path.basename(ext_path)[:-3]

            if name == "__init__":
                continue

            module = imp.load_source(name, ext_path)
            yield name, module

    def _discover_via_entry_points(self):
        for ep in pkg_resources.iter_entry_points('libraclient.extension'):
            name = ep.name
            module = ep.load()

            yield name, module

    def _add_bash_completion_subparser(self, subparsers):
        subparser = subparsers.add_parser(
            'bash_completion',
            add_help=False,
            formatter_class=OpenStackHelpFormatter
        )
        self.subcommands['bash_completion'] = subparser
        subparser.set_defaults(func=self.do_bash_completion)

    def _find_actions(self, subparsers, actions_module):
        for attr in (a for a in dir(actions_module) if a.startswith('do_')):
            # I prefer to be hypen-separated instead of underscores.
            command = attr[3:].replace('_', '-')
            callback = getattr(actions_module, attr)
            desc = callback.__doc__ or ''
            action_help = desc.strip()
            arguments = getattr(callback, 'arguments', [])

            subparser = subparsers.add_parser(
                command,
                help=action_help,
                description=desc,
                add_help=False,
                formatter_class=OpenStackHelpFormatter
            )
            subparser.add_argument(
                '-h', '--help',
                action='help',
                help=argparse.SUPPRESS,
            )
            self.subcommands[command] = subparser
            for (args, kwargs) in arguments:
                subparser.add_argument(*args, **kwargs)
            subparser.set_defaults(func=callback)

    def setup_debugging(self, debug):
        if not debug:
            return

        streamformat = "%(levelname)s (%(module)s:%(lineno)d) %(message)s"
        # Set up the root logger to debug so that the submodules can
        # print debug messages
        logging.basicConfig(level=logging.DEBUG,
                            format=streamformat)

    def main(self, argv):

        # Parse args once to find version and debug settings
        parser = self.get_base_parser()
        (options, args) = parser.parse_known_args(argv)
        self.setup_debugging(options.debug)

        # Discover available auth plugins
        auth.discover_auth_systems()

        # build available subcommands based on version
        self.extensions = self._discover_extensions(
            options.libra_api_version)

        self._run_extension_hooks('__pre_parse_args__')

        if '--endpoint_type' in argv:
            spot = argv.index('--endpoint_type')
            argv[spot] = '--endpoint-type'

        subcommand_parser = self.get_subcommand_parser(
            options.os_compute_api_version)
        self.parser = subcommand_parser

        if options.help or not argv:
            subcommand_parser.print_help()
            return 0

        args = subcommand_parser.parse_args(argv)
        self._run_extension_hooks('__post_parse_args__', args)

        # Short-circuit and deal with help right away.
        if args.func == self.do_help:
            self.do_help(args)
            return 0
        elif args.func == self.do_bash_completion:
            self.do_bash_completion(args)
            return 0

        os_username = args.os_username
        os_password = args.os_password
        os_tenant_name = args.os_tenant_name
        os_tenant_id = args.os_tenant_id
        os_auth_url = args.os_auth_url
        os_region_name = args.os_region_name
        os_auth_system = args.os_auth_system
        endpoint_type = args.endpoint_type
        insecure = args.insecure
        service_type = args.service_type
        service_name = args.service_name
        os_cache = args.os_cache
        cacert = args.os_cacert
        timeout = args.api_timeout

        if not os_auth_system:
            os_auth_system = 'keystone2'

        auth_plugin = auth.load_plugin(os_auth_system)

        os_password = None

        #FIXME(usrleon): Here should be restrict for project id same as
        # for os_username or os_password but for compatibility it is not.
        if not cliutils.isunauthenticated(args.func):
            if auth_plugin:
                auth_plugin.parse_opts(args)

            if not auth_plugin or not auth_plugin.opts:
                if not os_username:
                    raise exc.CommandError(
                        "You must provide a username"
                        " via either --os-username or env[OS_USERNAME]")

            if not os_tenant_name and not os_tenant_id:
                raise exc.CommandError(
                    "You must provide a tenant name "
                    "or tenant id via --os-tenant-name, "
                    "--os-tenant-id, env[OS_TENANT_NAME] "
                    "or env[OS_TENANT_ID]")

            if not os_auth_url:
                if os_auth_system and os_auth_system != 'keystone':
                    os_auth_url = auth_plugin.get_auth_url()

            if not os_auth_url:
                    raise exc.CommandError(
                        "You must provide an auth url "
                        "via either --os-auth-url or env[OS_AUTH_URL] "
                        "or specify an auth_system which defines a "
                        "default url with --os-auth-system "
                        "or env[OS_AUTH_SYSTEM]")

        if not (os_tenant_name or os_tenant_id):
            raise exc.CommandError(
                "You must provide a tenant_id "
                "via either --os-tenant-id or env[OS_TENANT_ID]")

        if not os_auth_url:
            raise exc.CommandError(
                "You must provide an auth url "
                "via either --os-auth-url or env[OS_AUTH_URL]")

        http_client = client.HTTPClient(
            auth_plugin,
            region_name=os_region_name,
            endpoint_type=endpoint_type,
            debug=args.debug,
            verify=args.insecure)

        self.cs = VersionedClient(
            options.libra_api_version,
            http_client,
            endpoint_type=endpoint_type,
            service_type=service_type)

        # Now check for the password/token of which pieces of the
        # identifying keyring key can come from the underlying client
        if not cliutils.isunauthenticated(args.func):
            helper = SecretsHelper(args, self.cs.http_client)

            if not args.os_token and not args.os_tenant_id:
                if helper.tenant_id and helper.auth_token and helper.endpoint:
                    auth_plugin.opts.update({
                        'tenant_id': helper.tenant_id,
                        'token': helper.auth_token,
                        'bypass_url': helper.endpoint})
                else:
                    # Auth using token must have failed or not happened
                    # at all, so now switch to password mode and save
                    # the token when its gotten... using our keyring
                    # saver
                    auth_plugin.opts['password'] = helper.password
                    self.cs.http_client.keyring_saver = helper
                    self.cs.http_client.authenticate()
            else:
                # If we're in token mode but no bypass_url we should auth..
                if not args.os_bypass_url:
                    self.cs.http_client.authenticate()
        try:
            args.func(self.cs, args)
        except exc.Unauthorized:
            raise exc.CommandError("Invalid OpenStack libra credentials.")
        except exc.AuthorizationFailure, e:
            raise exc.CommandError("Unable to authorize user")

        if args.timings:
            self._dump_timings(self.cs.get_timings())

    def _dump_timings(self, timings):
        class Tyme(object):
            def __init__(self, url, seconds):
                self.url = url
                self.seconds = seconds
        results = [Tyme(url, end - start) for url, start, end in timings]
        total = 0.0
        for tyme in results:
            total += tyme.seconds
        results.append(Tyme("Total", total))
        cliutils.print_list(results, ["url", "seconds"], sortby_index=None)

    def _run_extension_hooks(self, hook_type, *args, **kwargs):
        """Run hooks for all registered extensions."""
        for extension in self.extensions:
            extension.run_hooks(hook_type, *args, **kwargs)

    def do_bash_completion(self, _args):
        """
        Prints all of the commands and options to stdout so that the
        libra.bash_completion script doesn't have to hard code them.
        """
        commands = set()
        options = set()
        for sc_str, sc in self.subcommands.items():
            commands.add(sc_str)
            for option in sc._optionals._option_string_actions.keys():
                options.add(option)

        commands.remove('bash-completion')
        commands.remove('bash_completion')
        print(' '.join(commands | options))

    @cliutils.arg('command', metavar='<subcommand>', nargs='?',
                  help='Display help for <subcommand>')
    def do_help(self, args):
        """
        Display help about this program or one of its subcommands.
        """
        if args.command:
            if args.command in self.subcommands:
                self.subcommands[args.command].print_help()
            else:
                raise exc.CommandError("'%s' is not a valid subcommand" %
                                       args.command)
        else:
            self.parser.print_help()


def main():
    try:
        if sys.version_info >= (3, 0):
            LibraShell().main(sys.argv[1:])
        else:
            LibraShell().main(map(strutils.safe_decode,
                              sys.argv[1:]))
    except KeyboardInterrupt:
        print("... terminating libra client", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        logger.debug(e, exc_info=1)
        msg = 'ERROR: %s' % e.message

        if hasattr(e, 'details'):
            msg = '%s, DETAILS: %s' % (msg, e.details)
        if not isinstance(msg, six.string_types):
            msg = str(msg)
        print("%s" % strutils.safe_encode(msg), file=sys.stderr)
        sys.exit(1)
