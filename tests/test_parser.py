# coding=utf8

import unittest

from l20n.format.parser import FTLParser
from l20n.util import ftl


class TestPosition(unittest.TestCase):
    def setUp(self):
        self.ftl_parser = FTLParser()

    def test_simple_values(self):
        content = ftl('''
            foo = Foo
            bar = Bar
        ''')
        ast, _ = self.ftl_parser.parse(content, pos=True)

        foo, bar = ast.body
        self.assertEqual(
            content[foo.id._pos['start']:foo.id._pos['end']],
            'foo')
        self.assertEqual(
            content[foo.value._pos['start']:foo.value._pos['end']],
            'Foo')
        self.assertEqual(
            content[bar.id._pos['start']:bar.id._pos['end']],
            'bar')
        self.assertEqual(
            content[bar.value._pos['start']:bar.value._pos['end']],
            'Bar')

    def test_complex_values(self):
        content = ftl('''
            foo = Foo { bar }
                [bar]  AAA { $num ->
                           [one] One
                          *[other] Many { NUMBER($num) }
                       } BBB
        ''')
        ast, _ = self.ftl_parser.parse(content, pos=True)

        foo,  = ast.body
        placable = foo.value.elements[1]
        bar_trait, = foo.traits
        self.assertEqual(
            content[foo.id._pos['start']:foo.id._pos['end']],
            'foo')
        self.assertEqual(
            content[foo.value._pos['start']:foo.value._pos['end']],
            'Foo { bar }')
        self.assertEqual(
            content[placable._pos['start']:placable._pos['end']],
            '{ bar }')
        # TODO, expressions in placables don't have source data
        expression, = placable.expressions
        self.assertEqual(expression._pos, False)
        self.assertEqual(
            content[bar_trait.key._pos['start']:bar_trait.key._pos['end']],
            'bar')
        self.assertEqual(
            content[bar_trait.value._pos['start']:bar_trait.value._pos['end']],
            bar_trait.value.source)

