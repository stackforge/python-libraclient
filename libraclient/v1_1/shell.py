import argparse
from libraclient.openstack.common import cliutils


def _format_node(node):
    return '{status}/{condition} - {id} - {address}:{port}'.format(**node)


@cliutils.arg('id',
    type=str,
    help='ID to get')
def do_show(cs, args):
    lb = cs.loadbalancers.get(args.id)

    info = {}
    info.update(lb._info)
    info['nodes'] = "\n".join(map(_format_node, lb._info['nodes']))

    cliutils.print_dict(info, 'Load Balancer')


@cliutils.arg('id',
    type=str,
    help='ID to show Virtual IPs for.')
def do_virtualips(cs, args):
    vips = cs.loadbalancers.list_vip(args.id)



@cliutils.arg('--deleted',
           default=False,
           action='store_true',
           help='Display deleted LBs.')
def do_list(cs, args):
    lbs = cs.loadbalancers.list(deleted=args.deleted)
    cliutils.print_list(lbs, ['ID', 'Name', 'Protocol', 'Port', 'Status',
                        'Algorithm', 'Created', 'Updated', 'nodeCount'])


@cliutils.arg('id',
    type=int,
    help='ID to delete')
def do_delete(cs, args):
    cs.loadbalancers.delete(args.id)


def do_limits_list(cs, args):
    limits = cs.limits.get_limits()
    import ipdb
    ipdb.set_trace()
    cliutils.print_dict(limits[0])


def do_protocol_list(cs, args):
    protocols = cs.protocols.list()
    cliutils.print_list(protocols, fields)