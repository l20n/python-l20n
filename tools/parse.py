#!/usr/bin/python 

import sys

sys.path.append('./')
import codecs
import l20n.format.parser
import l20n.format.ast
import json

def read_file(path):
    with codecs.open(path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

def print_ast(fileType, data):
    l20nParser = l20n.format.parser.L20nParser()
    ast = l20nParser.parse(data)
    print(json.dumps(ast.toJSON(), indent=2, ensure_ascii=False))

    print('Errors:')
    for error in ast._errors:
        print(error.message)

if __name__ == "__main__":
    file_type = 'l20n'
    f = read_file(sys.argv[1])
    print_ast(file_type, f)
