# coding=utf8

import unittest

from l20n.migrate.cldr import get_plural_categories


class TestPluralCategories(unittest.TestCase):
    def test_known_language(self):
        self.assertEqual(
            get_plural_categories('pl'),
            ('one', 'few', 'many', 'other')
        )

    def test_fallback_one(self):
        self.assertEqual(
            get_plural_categories('ga-IE'),
            ('one', 'two', 'few', 'many', 'other')
        )

    def test_fallback_two(self):
        self.assertEqual(
            get_plural_categories('ja-JP-mac'),
            ('other',)
        )

    def test_unknown_language(self):
        with self.assertRaisesRegexp(RuntimeError, 'Unknown language'):
            get_plural_categories('i-default')
