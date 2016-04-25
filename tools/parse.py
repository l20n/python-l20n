#!/usr/bin/python 

import sys

sys.path.append('./')
import codecs
import ftl.format.parser
import ftl.format.ast
import json

def read_file(path):
    with codecs.open(path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

def print_ast(fileType, data):
    ftlParser = ftl.format.parser.FTLParser()
    ast = ftlParser.parseResource(data)
    print(json.dumps(ast.toJSON(), indent=2, ensure_ascii=False))

    print('Errors:')
    for error in ast._errors:
        print(error.message)

if __name__ == "__main__":
    file_type = 'ftl'
    f = read_file(sys.argv[1])
    print_ast(file_type, f)
