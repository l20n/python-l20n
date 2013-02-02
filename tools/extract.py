#!/usr/bin/env python2

import sys
from l20n.format.lol import ast
from l20n.format.lol.serializer import Serializer
from BeautifulSoup import BeautifulSoup

ATTRS = (
    'id',
    'data-l10n-id',
    'type',
    'class',
    'style',
    'href',
)

isloc = lambda attr: attr[0] not in ATTRS

def extract(node):
    id = ast.Identifier(node['data-l10n-id'])
    attrs2 = filter(isloc, node.attrs)
    attrs = {}
    for i in attrs2:
        attrs[i[0]] = ast.Attribute(ast.Identifier(i[0]),
                                    ast.String(i[1]))
    for child in node.findAll():
        child.attrs = filter(isloc, child.attrs)
    value = ast.String(node.renderContents())
    return id, value, attrs

if __name__ == '__main__':
    f = open(sys.argv[1], 'r')
    dom = BeautifulSoup(f)
    nodes = dom.findAll(True, {'data-l10n-id': True})
    lol = ast.LOL()
    for node in nodes:
        id, value, attrs = extract(node)
        entity = ast.Entity(id, None, value, attrs)
        lol.body.append(entity)
    print(Serializer.serialize(lol))

