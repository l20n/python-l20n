#!/usr/bin/python 

import sys

sys.path.append('./lib')
import codecs
import l20n.format.parser
import l20n.format.serializer
import json

def read_file(path):
    with codecs.open(path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

def print_l20n(fileType, data):
    print('----- ORIGINAL -----')
    print(data)
    l20nParser = l20n.format.parser.Parser()
    print('----- AST -----')
    ast = l20nParser.parse(data)
    print(json.dumps(ast, indent=2))
    print('--------------------')
    l20nSerializer = l20n.format.serializer.Serializer()
    result = l20nSerializer.serialize(ast)
    print(result)
if __name__ == "__main__":
      file_type = 'l20n'
      f = read_file(sys.argv[1])
      print_l20n(file_type, f)

