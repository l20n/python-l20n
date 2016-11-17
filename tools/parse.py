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
    ftlParser = l20n.format.parser.FTLParser()
    [ast, errors] = ftlParser.parseResource(data)
    print(json.dumps(ast, indent=2, ensure_ascii=False))

    print('Errors:')
    for error in errors:
        print(error.message)

if __name__ == "__main__":
    file_type = 'ftl'
    f = read_file(sys.argv[1])
    print_ast(file_type, f)
