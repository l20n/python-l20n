import unittest
import sys
import os
import codecs
import json

path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(path, '..', '..'))

basePath = '/home/zbraniecki/projects/l20n/js/test/lib/fixtures/parser/ftl'

from ftl.format.parser import FTLParser

def read_file(path):
    with codecs.open(path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

class L20nParserTestCase(unittest.TestCase):

    def setUp(self):
        self.parser = FTLParser()
        self.maxDiff = None

    def test_fixtures(self):

        for dirpath, dirnames, filenames in os.walk(basePath):
            for f in filenames:
                if not f.endswith('.ftl'):
                    continue
                ftlPath = os.path.join(dirpath, f)
                jsonPath = ftlPath[:-4] + '.ast.json'

                source = read_file(ftlPath)
                jsonSource = read_file(jsonPath)
                [ast, errors] = self.parser.parseResource(source)
                refAST = json.loads(jsonSource)
                self.assertEqual(ast, refAST, 'Error in fixture: ' + f)


if __name__ == '__main__':
    unittest.main()
