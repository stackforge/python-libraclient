import argparse
from libraclient.openstack.common import cliutils
from libraclient import utils


def _format_node(node):
    return '{status}/{condition} - {id} - {address}:{port}'.format(**node)


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
