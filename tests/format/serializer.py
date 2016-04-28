import unittest
import sys
import os
import codecs
import json

path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(path, '..', '..'))

basePath = '/home/zbraniecki/projects/l20n/js/test/lib/fixtures/parser/ftl'

from ftl.format.parser import FTLParser
from ftl.format.serializer import FTLSerializer

def read_file(path):
    with codecs.open(path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

class L20nParserTestCase(unittest.TestCase):

    def setUp(self):
        self.parser = FTLParser()
        self.serializer = FTLSerializer()
        self.maxDiff = None

    def test_fixtures(self):

        for dirpath, dirnames, filenames in os.walk(basePath):
            for f in filenames:
                if not f.endswith('.ftl') or 'error' in f:
                    continue
                ftlPath = os.path.join(dirpath, f)

                source = read_file(ftlPath)
                ast = self.parser.parseResource(source)
                out = self.serializer.serialize(ast)
                ast2 = self.parser.parseResource(out)
                self.assertEqual(ast.toJSON()['body'], ast2.toJSON()['body'], 'Error in fixture: ' + f)


if __name__ == '__main__':
    unittest.main()
