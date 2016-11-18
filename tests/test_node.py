# coding=utf8

import unittest

from l20n.format.parser import FTLParser
from l20n.util import ftl


class TestTraverse(unittest.TestCase):
    def setUp(self):
        self.ftl_parser = FTLParser()

    def test_simple_values(self):
        ast, _ = self.ftl_parser.parse(ftl('''
            foo = Foo
            bar = Bar
        '''))

        self.assertEqual(
            ast.traverse(lambda x: x).toJSON(),
            ast.toJSON()
        )

    def test_complex_values(self):
        ast, _ = self.ftl_parser.parse(ftl('''
            foo = Foo
            foo = Foo { bar }
                [bar]  AAA { $num ->
                           [one] One
                          *[other] Many { NUMBER($num) }
                       } BBB
        '''))

        self.assertEqual(
            ast.traverse(lambda x: x).toJSON(),
            ast.toJSON()
        )
