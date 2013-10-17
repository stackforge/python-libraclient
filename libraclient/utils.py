import textwrap
import prettytable
from libraclient.openstack.common import strutils


def _field(orig_field, titled=True):
    """
    Allow for writin short-hand field stuff like n='server', dn='Server'
    """
    field = {}

    aliases = {
        'n': 'name',
        'dn': 'display',
        'f': 'formatter'
    }
    if isinstance(orig_field, dict):
        for alias, name in aliases.items():
            if alias in orig_field:
                field[name] = orig_field[alias]
            elif name in orig_field:
                field[name] = orig_field[name]
    elif isinstance(orig_field, basestring):
        field['name'] = orig_field
    elif isinstance(orig_field, tuple):
        field['name'], field['display'] = orig_field

    if 'display' not in field:
        dn = field['name']
        if titled:
            dn = dn.title()
        field['display'] = dn
    return field


def _get_fields(obj):
    # NOTE: Resource class
    try:
        i = obj._info
    except AttributeError:
        pass
    # NOTE: dict
    if isinstance(obj, dict):
        i = obj
    return [{'name': n} for n in i.keys()]


def create_row(obj, fields=None, titled=False):
    """
    :param obj: a :class:`dict` or :class:`Resource`
    :param fields: A :class:`list` of :class:`dicts` describing fields to do.
                   Default: obj.keys() if dict
    :param formatters: Field formatters.
    """
    fields = [_field(f, titled=titled) for f in fields or _get_fields(obj)]

    row = []
    for field in fields:
        if 'formatter' in field:
            row.append(field['formatter'](obj[field['name']]))
        else:
            if isinstance(obj, dict):
                fv = obj[field['name']]
            elif hasattr(obj, '_info'):
                fv = getattr(obj, field['name'])
            row.append(fv)
    return row


def print_list(objs, fields=None, sort_by=None, titled=False):
    # If no fields are given use objs[0]
    fields = [_field(f, titled=titled) for f in fields or _get_fields(objs[0])]

    # Set the display names for headers.
    field_names = [f['display'] for f in fields]

    # Sort by column
    if sort_by is None:
        sortby = None
    else:
        sortby = fields[sortby_index]
    pt = prettytable.PrettyTable(field_names, caching=False)
    pt.align = 'l'

    for o in objs:
        row = create_row(o, fields=fields, titled=False)
        pt.add_row(row)
    print(strutils.safe_encode(pt.get_string(sortby=sortby)))
