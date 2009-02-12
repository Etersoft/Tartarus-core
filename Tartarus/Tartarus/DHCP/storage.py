from lxml import etree
from internal import Identity, STATIC, TRUST, UNTRUST

def save(server, file):
    tree = etree.ElementTree(etree.Element('dhcp'))
    root_node = tree.getroot()
    sol = etree.SubElement(root_node, 'start-on-load')
    if server.startOnLoad():
        sol.text = 'True'
    else:
        sol.text = 'False'
    _add_params(server.params(), root_node)
    for h in server.hosts().itervalues():
        host_node = etree.SubElement(root_node, 'host', name=h.name())
        if h.identity().type() is Identity.IDENTITY:
            etree.SubElement(host_node, 'id').text = h.identity().id()
        else:
            etree.SubElement(host_node, 'hardware').text = h.identity().hardware()
        _add_params(h.params(), host_node)
    for s in server.subnets().itervalues():
        sbn_node = etree.SubElement(root_node, 'subnet')
        sbn_node.set('id', s.id())
        sbn_node.set('decl', s.decl())
        _add_range(STATIC, s.range(STATIC), sbn_node)
        _add_range(TRUST, s.range(TRUST), sbn_node)
        _add_range(UNTRUST, s.range(UNTRUST), sbn_node)
        _add_params(s.params(), sbn_node)
    tree.write(file, pretty_print=True)

def load(server, file):
    tree = etree.parse(file)
    root_node = tree.getroot()
    sol = root_node.find('start-on-load')
    if sol.text == 'True':
        server.startOnLoad(True)
    else:
        server.startOnLoad(False)
    _get_params(server.params(), root_node)
    for host_node in root_node.findall('host'):
        name = host_node.get('name')
        id_node = host_node.find('id')
        if id_node is not None:
            id = Identity(id=id_node.text)
        else:
            id = Identity(hardware=host_node.find('hardware').text)
        host = server.addHost(name, id)
        _get_params(host.params(), host_node)
    for sbn_node in root_node.findall('subnet'):
        id = sbn_node.get('id')
        decl = sbn_node.get('decl')
        sbn = server.restoreSubnet(id, decl)
        _get_params(sbn.params(), sbn_node)
        for type, start, end in _get_range(sbn_node):
            sbn.range(type, (start, end))

def _add_range(type, range, node):
    if range is not ():
        start, end = range
        etree.SubElement(node, 'range', type=str(type), start=start, end=end)

def _get_range(node):
    for r in node.findall('range'):
        yield int(r.get('type')), r.get('start'), r.get('end')

def _add_params(params, node):
    for key, value in params.iter():
        n = etree.SubElement(node, 'param')
        etree.SubElement(n, 'key').text = key
        etree.SubElement(n, 'value').text = value

def _get_params(params, node):
    for p in node.findall('param'):
        key = p.find('key').text
        value = p.find('value').text
        params.set(key, value)

