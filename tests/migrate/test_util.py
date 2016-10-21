# coding=utf8

import unittest

import l20n.format.ast as FTL
from l20n.util import fold
from l20n.migrate.transforms import CONCAT, COPY, SOURCE


def get_source(acc, cur):
    if isinstance(cur, SOURCE):
        return acc + ((cur.path, cur.key),)
    return acc


class TestTraverse(unittest.TestCase):
    def test_copy_concat(self):
        node = FTL.Entity(
            FTL.Identifier('hello'),
            value=CONCAT(
                COPY(
                    SOURCE('path1', 'key1')
                ),
                COPY(
                    SOURCE('path2', 'key2')
                )
            )
        )

        result = node.traverse(lambda x: x)

        self.assertEqual(
            result.value.patterns[0].source.key,
            'key1'
        )
        self.assertEqual(
            result.value.patterns[1].source.key,
            'key2'
        )


class TestReduce(unittest.TestCase):
    def test_copy_value(self):
        node = FTL.Entity(
            id=FTL.Identifier('key'),
            value=COPY(
                SOURCE('path', 'key')
            )
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
                    value=COPY(
                        SOURCE('path1', 'key1')
                    )
                ),
                FTL.Member(
                    FTL.Keyword('trait2'),
                    value=COPY(
                        SOURCE('path2', 'key2')
                    )
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
                COPY(
                    SOURCE('path1', 'key1')
                ),
                COPY(
                    SOURCE('path2', 'key2')
                )
            )
        )

        self.assertEqual(
            fold(get_source, node, ()),
            (('path1', 'key1'), ('path2', 'key2'))
        )
