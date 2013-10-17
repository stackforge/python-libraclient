import argparse
from libraclient.openstack.common import cliutils
from libraclient import utils


NODE_FIELDS = ["id", "address", "port", "condition", "status"]


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

    lb = cs.loadbalancers.create(
        name=args.name,
        port=args.port,
        protocol=args.protocol,
        algorithm=args.algorithm,
        nodes=args.node,
        virtual_ip=args.vip)
    cliutils.print_dict(lb._info)


@cliutils.arg(
    'id',
    type=str,
    help='ID to get')
def do_show(cs, args):
    lb = cs.loadbalancers.get(args.id)

    info = {}
    info.update(lb._info)
    info['nodes'] = "\n".join(map(cs.loadbalancers.format_node, lb._info['nodes']))

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
        algorithm=args.algorithm)

do_modify = do_update


@cliutils.arg(
    'id',
    type=int,
    help='ID to delete')
def do_delete(cs, args):
    cs.loadbalancers.delete(args.id)


@cliutils.arg('id', help='load balancer ID')
@cliutils.arg('--node', help='node to add in ip:port form',
                required=True, action='append')
def do_node_add(cs, args):
    nodes = cs.loadbalancers.create_node(args.id, args.node)
    cs.print_list(nodes, fields=NODE_FIELDS)


@cliutils.arg(
    'lb_id',
    type=str,
    help='ID of the LoadBalancer the Nodes belongs to.')
def do_node_list(cs, args):
    """
    List LoadBalancer Nodes.
    """
    nodes = cs.loadbalancers.list_nodes(args.lb_id)
    fields = ["id", "address", "port", "condition", "status"]
    utils.print_list(nodes, fields=fields, titled=True)


@cliutils.arg(
    'lb_id',
    type=str,
    help='ID of the LoadBalancer that the Node belongs to.')
@cliutils.arg(
    'node_id',
    type=str,
    help='ID of the Node to show.')
def do_node_show(cs, args):
    """
    Show a Node belonging to a LoadBalancer.
    """
    node = cs.loadbalancers.get_node(args.lb_id, args.node_id)
    cliutils.print_dict(node._info)


@cliutils.arg(
    'lb_id',
    type=str,
    help='ID of the LoadBalancer the Nodes belongs to.')
@cliutils.arg(
    'node_id',
    help='node ID to modify')
@cliutils.arg(
    '--condition',
    help='the new state for the node',
    choices=['ENABLED', 'DISABLED'])
@cliutils.arg(
    '--weight',
    type=int,
    default=1,
    metavar='COUNT',
    help='node weight ratio as compared to other nodes')
def do_node_update(cs, args):
    cs.loadbalancers.update_node(
        args.lb_id, args.node_id, condition=args.condition, weight=args.weight)


@cliutils.arg(
    'lb_id',
    type=str,
    help='ID of the LoadBalancer that the Node belongs to.')
@cliutils.arg(
    'node_id',
    type=str,
    help='ID of the Node to show.')
def do_node_delete(cs, args):
    """
    Delete a Node belonging to a LoadBalancer
    """
    cs.loadbalancers.delete_node(args.lb_id, args.node_id)


@cliutils.arg(
    'lb_id',
    type=str,
    help='ID of the LoadBalancer that the Node belongs to.')
def do_momitor_show(cs, args):
    monitor = cs.loadbalancers.get_monitor(args.lb_id)
    cliutils.print_dict(monitor._info)


@cliutils.arg(
    'lb_id',
    type=str,
    help='ID of the LoadBalancer that the Node belongs to.')
@cliutils.arg(
    '--type',
    choices=['CONNECT', 'HTTP'],
    default='CONNECT',
    help='health monitor type')
@cliutils.arg(
    '--delay',
    type=int,
    default=30,
    metavar='SECONDS',
    help='time between health monitor calls')
@cliutils.arg(
    '--timeout',
    type=int,
    default=30,
    metavar='SECONDS',
    help='time to wait before monitor times out')
@cliutils.arg(
    '--attempts',
    type=int,
    default=2,
    metavar='COUNT',
    help='connection attempts before marking node as bad')
@cliutils.arg(
    '--path',
    help='URI path for health check')
def do_monitor_update(cs, args):
    monitor = cs.loadbalancers.update_monitor(
        args.lb_id, type_=args.type, delay=args.delay, timeout=args.timeout,
        attempts=args.attempts, path=args.path)
    cliutils.print_dict(monitor._info)


@cliutils.arg(
    'lb_id',
    type=str,
    help='ID of the LoadBalancer that the Node belongs to.')
def do_monitor_delete(cs, args):
    cs.loadbalancers.delete_monitor(args.lb_id)


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


# Non LB specific commands
def do_algorithm_list(cs, args):
    algs = cs.algorithms.list()
    fields = [('name', 'Algorithm Name')]
    utils.print_list(algs, fields=fields)


# TODO: Figure out the printing of this one
def do_limit_list(cs, args):
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


def do_protocol_list(cs, args):
    protocols = cs.protocols.list()
    utils.print_list(protocols, titled=True)

@cliutils.arg('id', help='load balancer ID', required=True)
@cliutils.arg('--storage', help='storage type', choices=['Swift'])
@cliutils.arg('--endpoint', help='object store endpoint to use')
@cliutils.arg('--basepath', help='object store based directory')
@cliutils.arg('--token', help='object store authentication token')
def do_logs(cs, args):
    data = {}
    if args.storage:
        data['objectStoreType'] = args.storage
    if args.endpoint:
        data['objectStoreEndpoint'] = args.endpoint
    if args.basepath:
        data['objectStoreBasePath'] = args.basepath
    if args.token:
        data['authToken'] = args.token
    cs.loadbalancers,send_logs(args.id, data)