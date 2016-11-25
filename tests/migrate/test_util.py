# coding=utf8

import unittest

import l20n.format.ast as FTL
from l20n.util import fold
from l20n.migrate.transforms import CONCAT, LITERAL_FROM, SOURCE


def get_source(acc, cur):
    if isinstance(cur, SOURCE):
        return acc + ((cur.path, cur.key),)
    return acc


class TestTraverse(unittest.TestCase):
    def test_copy_concat(self):
        node = FTL.Entity(
            FTL.Identifier('hello'),
            value=CONCAT(
                LITERAL_FROM('path1', 'key1'),
                LITERAL_FROM('path2', 'key2')
            )
        )

        result = node.traverse(lambda x: x)

        self.assertEqual(
            result.value.patterns[0].key,
            'key1'
        )
        self.assertEqual(
            result.value.patterns[1].key,
            'key2'
        )


class TestReduce(unittest.TestCase):
    def test_copy_value(self):
        node = FTL.Entity(
            id=FTL.Identifier('key'),
            value=LITERAL_FROM('path', 'key')
        )

        self.assertEqual(
            fold(get_source, node, ()),
            (('path', 'key'),)
        )

    def test_copy_traits(self):
        node = FTL.Entity(
            id=FTL.Identifier('key'),
            traits=[
                FTL.Member(
                    FTL.Keyword('trait1'),
                    value=LITERAL_FROM('path1', 'key1')
                ),
                FTL.Member(
                    FTL.Keyword('trait2'),
                    value=LITERAL_FROM('path2', 'key2')
                )
            ]
        )

        self.assertEqual(
            fold(get_source, node, ()),
            (('path1', 'key1'), ('path2', 'key2'))
        )

    def test_copy_concat(self):
        node = FTL.Entity(
            FTL.Identifier('hello'),
            value=CONCAT(
                LITERAL_FROM('path1', 'key1'),
                LITERAL_FROM('path2', 'key2')
            )
        )

        self.assertEqual(
            fold(get_source, node, ()),
            (('path1', 'key1'), ('path2', 'key2'))
        )
