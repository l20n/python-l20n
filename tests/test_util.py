# coding=utf8

import unittest

import l20n.format.ast as FTL
from l20n.util import fold


class TestReduce(unittest.TestCase):
    def test_pattern(self):
        node = FTL.Entity(
            id=FTL.Identifier('key'),
            value=FTL.Pattern(
                source=None,
                elements=[
                    FTL.TextElement('Value')
                ]
            )
        )

        def get_value(acc, cur):
            if isinstance(cur, FTL.TextElement):
                return acc + (cur.value,)
            return acc

        self.assertEqual(
            fold(get_value, node, ()),
            ('Value',)
        )
