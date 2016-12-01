#!/usr/bin/python 
# coding=utf-8

import sys, os

sys.path.append('./')
import codecs
import l20n.format.parser
import l20n.format.serializer
import json

def read_file(path):
    with codecs.open(path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

def print_l20n(fileType, data):
    l20nSerializer = l20n.format.serializer.FTLSerializer()
    result = None

    if fileType == 'json':
        result = l20nSerializer.serialize(json.loads(data))
    elif fileType == 'ftl':
        #print('----- ORIGINAL -----')
        #print(data)
        l20nParser = l20n.format.parser.FTLParser()
        #print('----- AST -----')
        [ast, errors] = l20nParser.parseResource(data)
        #print(json.dumps(ast, indent=2, ensure_ascii=False))
        #print('--------------------')
        result = l20nSerializer.serialize(ast)
    
    print(result.encode('utf-8'))

if __name__ == "__main__":
    fileName, fileExtension = os.path.splitext(sys.argv[1])
    f = read_file(sys.argv[1])
    print_l20n(fileExtension[1:], f)

