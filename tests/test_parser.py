# coding=utf8

import functools
import unittest

from l20n.format.parser import FTLParser
from l20n.format import ast
from l20n.util import ftl


class TestPosition(unittest.TestCase):
    def setUp(self):
        self.ftl_parser = FTLParser()

    def position_test(self, content, entities, placables, value):
        # traversal method testing positions and known node types
        if not isinstance(value, ast.Node):
            return value
        if not isinstance(value._pos, dict):
            # unpositioned content, that's OK
            return value
        pos_val = content[value._pos['start']:value._pos['end']]
        if isinstance(value, ast.Pattern):
            ref_val = value.source
        elif isinstance(value, ast.Keyword):
            ref_val = value.name
        elif isinstance(value, ast.TextElement):
            ref_val = value.value
        elif isinstance(value, ast.Identifier):
            ref_val = value.name
        elif isinstance(value, ast.Comment):
            ref_val = u'#{}'.format(value.content)
        elif isinstance(value, ast.Section):
            ref_val = u'[[ {} ]]'.format(value.key.name)
        elif isinstance(value, ast.Entity):
            # cheating this test, we'll test the entities explicitly
            ref_val = pos_val
            entities.append(pos_val)
        elif isinstance(value, ast.Placeable):
            # cheating this test, we'll test the placables explicitly
            ref_val = pos_val
            placables.append(pos_val)
        else:
            self.fail(u'Untested {}._pos referencing {}'.format(
                type(value).__name__, pos_val))
        self.assertEqual(pos_val, ref_val)
        return value

    def test_simple_values(self):
        content = ftl('''
            foo = Foo
            bar = Bar
        ''')
        resource, _ = self.ftl_parser.parse(content, pos=True)

        entities = []
        placables = []
        resource.traverse(
            functools.partial(self.position_test, content, entities, placables))

        # Test entities and placables
        self.assertListEqual(entities, [l+'\n' for l in content.splitlines()])
        self.assertListEqual(placables, [])

    def test_comment(self):
        content = ftl('''
            #something strange
            bar = Bar
        ''')
        resource, _ = self.ftl_parser.parse(content, pos=True)

        entities = []
        placables = []
        resource.traverse(
            functools.partial(self.position_test, content, entities, placables))

        # Test entities and placables
        self.assertListEqual(entities, ['bar = Bar\n'])
        self.assertListEqual(placables, [])

    def test_section(self):
        content = ftl('''
            [[ sec ]]
            bar = Bar
        ''')
        resource, _ = self.ftl_parser.parse(content, pos=True)

        entities = []
        placables = []
        resource.traverse(
            functools.partial(self.position_test, content, entities, placables))

        # Test entities and placables
        self.assertListEqual(entities, ['bar = Bar\n'])
        self.assertListEqual(placables, [])

    def test_complex_values(self):
        content = ftl('''
            foo = Foo { bar }
                [bar]  AAA { $num ->
                           [one] One
                          *[other] Many { NUMBER($num) }
                       } BBB
        ''')
        resource, _ = self.ftl_parser.parse(content, pos=True)

        entities = []
        placables = []
        resource.traverse(
            functools.partial(self.position_test, content, entities, placables))

        # Test the entities
        self.assertListEqual(entities, [content])

        # Test the placables now. The order of value and traits
        # isn't defined, so test { bar } first, remove it, and
        # then test the bar trait, depth first.
        self.assertIn('{ bar }', placables)
        placables.remove('{ bar }')
        self.assertIn(placables[0], placables[1])
        self.assertEqual(placables[0], '{ NUMBER($num) }')
