import argparse
from libraclient.openstack.common import cliutils
from libraclient import utils


def _format_node(node):
    return '{status}/{condition} - {id} - {address}:{port}'.format(**node)


@cliutils.arg(
    '--name',
    type=str,
    help='Name of the new LoadBalancer.',
    required=True)
@cliutils.arg(
    '--port',
    help='port for the load balancer, 80 is default')
@cliutils.arg(
    '--protocol',
    help='protocol for the load balancer, HTTP is default',
    choices=['HTTP', 'TCP', 'GALERA'])
@cliutils.arg(
    '--algorithm',
    help='algorithm for the load balancer,'
        ' ROUND_ROBIN is default',
    choices=['LEAST_CONNECTIONS', 'ROUND_ROBIN'])
@cliutils.arg(
    '--node',
    help='a node for the load balancer in ip:port format',
    action='append', required=True)
@cliutils.arg(
    '--vip',
    help='the virtual IP to attach the load balancer to')
def do_create(cs, args):
    data = {}
    data['name'] = args.name

    cs.loadbalancers.create(
        name=args.name,
        port=args.port,
        protocol=args.protocol,
        algorithm=args.algorithm,
        nodes=args.node,
        virtual_ips=args.vip)


@cliutils.arg(
    'id',
    type=str,
    help='ID to get')
def do_show(cs, args):
    lb = cs.loadbalancers.get(args.id)

    info = {}
    info.update(lb._info)
    info['nodes'] = "\n".join(map(_format_node, lb._info['nodes']))

    cliutils.print_dict(info, 'Load Balancer')


@cliutils.arg(
    '--deleted',
    default=False,
    action='store_true',
    help='Display deleted LBs.')
def do_list(cs, args):
    lbs = cs.loadbalancers.list(deleted=args.deleted)
    fields = [
        ('id', 'ID'),
        'name',
        'protocol',
        'port',
        'status',
        'algorithm',
        'created',
        'updated',
        ('nodeCount', 'Node Count')]
    utils.print_list(lbs, fields=fields, titled=True)


@cliutils.arg('id', help='load balancer ID')
@cliutils.arg('--name', help='new name for the load balancer')
@cliutils.arg('--algorithm',
                help='new algorithm for the load balancer',
                choices=['LEAST_CONNECTIONS', 'ROUND_ROBIN'])
def do_update(cs, args):
    cs.loadbalancers.update(
        args.id,
        name=args.name,
        algorithm=args.algorithm
        )

do_modify = do_update


@cliutils.arg(
    'id',
    type=int,
    help='ID to delete')
def do_delete(cs, args):
    cs.loadbalancers.delete(args.id)


# TODO: Figure out the printing of this one
def do_limits_list(cs, args):
    limits = cs.limits.list_limits()
    out = []
    for l in limits:
        info = l._info
        del info['name']
        info = "\n".join(['%s: %s' % (k, info[k])
                         for k in sorted(info.keys())])
        out.append({'name': l.name, 'info': info})
    fields = ['name', 'info']
    utils.print_list(out, fields=fields)


@cliutils.arg(
    'id',
    type=str,
    help='ID to show Virtual IPs for.')
def do_virtualips(cs, args):
    vips = cs.loadbalancers.list_vip(args.id)
    fields = [
        'id',
        'type',
        ('ipVersion', 'IP Version'),
        'address'
    ]
    utils.print_list(vips, fields=fields, titled=True)


def do_protocol_list(cs, args):
    protocols = cs.protocols.list()
    utils.print_list(protocols, titled=True)
