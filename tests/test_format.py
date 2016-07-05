import unittest
import os
import codecs
import json

from ftl.format.parser import FTLParser
from ftl.format.serializer import FTLSerializer

fixtures = os.path.join(
    os.path.dirname(__file__),
    'l20n-syntax-fixtures', 'parser', 'ftl')


def read_file(path):
    with codecs.open(path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text


class TestMeta(type):
    '''Metaclass to add test discovery'''
    def __new__(mcs, name, bases, dict):

        def gen_test(ftl):
            def test(self):
                self.process(ftl)
            return test
        for f in os.listdir(fixtures):
            ftl, ext = os.path.splitext(f)
            if ext != '.ftl':
                continue
            test_name = 'test_%s' % ftl.replace('-', '_')
            dict[test_name] = gen_test(ftl)

        return type.__new__(mcs, name, bases, dict)


class L20nParserTestCase(unittest.TestCase, metaclass = TestMeta):
    __metaclass__ = TestMeta

    def setUp(self):
        self.parser = FTLParser()
        self.maxDiff = None

    def process(self, ftl):
        ftlPath = os.path.join(fixtures, ftl + '.ftl')
        jsonPath = os.path.join(fixtures, ftl + '.ast.json')
        source = read_file(ftlPath)
        jsonSource = read_file(jsonPath)
        [ast, errors] = self.parser.parseResource(source)
        refAST = json.loads(jsonSource)
        self.assertEqual(ast, refAST, 'Error in fixture: ' + ftl)


class L20nSerializerTestCase(L20nParserTestCase):

    def setUp(self):
        L20nParserTestCase.setUp(self)
        self.serializer = FTLSerializer()

    def process(self, ftl):
        if 'error' in ftl:
            self.skipTest('Error tests not run in Serializer')
        ftlPath = os.path.join(fixtures, ftl + '.ftl')
        source = read_file(ftlPath)
        [ast, errors] = self.parser.parseResource(source)
        out = self.serializer.serialize(ast)
        [ast2, errors] = self.parser.parseResource(out)
        self.assertEqual(ast['body'], ast2['body'], 'Error in fixture: ' + ftl)


if __name__ == '__main__':
    unittest.main()
