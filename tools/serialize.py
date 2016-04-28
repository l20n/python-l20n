#!/usr/bin/python 

import sys, os

sys.path.append('./')
import codecs
import ftl.format.parser
import ftl.format.serializer
import json

def read_file(path):
    with codecs.open(path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

def print_l20n(fileType, data):
    l20nSerializer = ftl.format.serializer.FTLSerializer()
    result = None

    if fileType == 'json':
        result = l20nSerializer.serialize(json.loads(data))
    elif fileType == 'ftl':
        print('----- ORIGINAL -----')
        print(data)
        l20nParser = ftl.format.parser.FTLParser()
        print('----- AST -----')
        ast = l20nParser.parseResource(data)
        print(json.dumps(ast, indent=2, ensure_ascii=False))
        print('--------------------')
        result = l20nSerializer.serialize(ast)
    
    print(result)

if __name__ == "__main__":
    fileName, fileExtension = os.path.splitext(sys.argv[1])
    f = read_file(sys.argv[1])
    print_l20n(fileExtension[1:], f)

