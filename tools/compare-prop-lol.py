#!/usr/bin/python 
import sys
import codecs
import mozilla.format.properties.parser
import l20n.format.lol.parser
import l20n.format.lol.ast
from collections import OrderedDict

def read_file(path):
    with codecs.open(path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

def update_id(id):
    return id.replace('-','_')

def update_prop(prop):
    newprop = {}
    for i in prop.keys():
        id = update_id(i)
        val = prop[i]['value']
        if id.find('.') != -1:
            id, attr = id.split('.')
            if id not in newprop:
                newprop[id] = {'id': id, 'value': None, 'attrs': {}}
            newprop[id]['attrs'][attr] = val
        else:
            if id not in newprop:
                newprop[id] = {'id': id, 'value': None, 'attrs': {}}
            newprop[id]['value'] = val
    return newprop

def compare(path1, path2):
    diff = {
      'obsolete': [],
      'missing': [],
      'modified': []
    }
    prop_source = read_file(path1)
    lol_source = read_file(path2)

    prop_parser = mozilla.format.properties.parser.Parser()
    prop = prop_parser.parse_to_entitylist(prop_source)

    prop = update_prop(prop)

    lol_parser = l20n.format.lol.parser.Parser()
    lol = lol_parser.parse(lol_source)
    
    lol_entities = OrderedDict()
    for i in lol.body:
        if isinstance(i, l20n.format.lol.ast.Entity):
            lol_entities[i.id.name] = i

    for i in prop.keys():
        if i not in lol_entities:
            diff['missing'].append(prop[i])
        else:
            val = lol_entities[i].value
            if val is not None:
                val = str(val)
            if prop[i]['value'] != val:
                ediff = {
                    'id': i,
                    'value': [prop[i]['value'], val],
                    'attrs': OrderedDict()
                }
                diff['modified'].append(ediff)
    for i in lol_entities.keys():
        if i not in prop:
            diff['obsolete'].append(lol_entities[i])
    return diff

if __name__ == "__main__":
    diff = compare(sys.argv[1], sys.argv[2])

    if diff['missing']:
        print('missing:')
        for i in diff['missing']:
            print('  %s' % i['id'])
    if diff['obsolete']:
        print('obsolete:')
        for i in diff['obsolete']:
            print('  %s' % i.id)
    if diff['modified']:
        print('modified:')
        for i in diff['modified']:
            print('  %s - {"%s" -> "%s"}' % (i['id'], i['value'][0], i['value'][1]))
