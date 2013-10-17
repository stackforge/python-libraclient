import argparse
from libraclient.openstack.common import cliutils


def _format_node(node):
    return '{status}/{condition} - {id} - {address}:{port}'.format(**node)


@cliutils.arg('id',
    type=str,
    help='ID to get')
def do_show(cs, args):
    lb = cs.lb.get(args.id)

    info = {}
    info.update(lb._info)
    info['nodes'] = "\n".join(map(_format_node, lb._info['nodes']))

    cliutils.print_dict(info, 'Load Balancer')


@cliutils.arg('--deleted',
           default=False,
           action='store_true',
           help='Display deleted LBs.')
def do_list(cs, args):
    lbs = cs.lb.list(deleted=args.deleted)
    cliutils.print_list(lbs, ['ID', 'Name', 'Protocol', 'Port', 'Status',
                        'Algorithm', 'Created', 'Updated', 'nodeCount'])


@cliutils.arg('id',
    type=int,
    help='ID to delete')
def do_delete(cs, args):
    cs.lb.delete(args.id)