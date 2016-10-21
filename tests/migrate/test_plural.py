# coding=utf8

import unittest

import l20n.format.ast as FTL
from compare_locales.parser import PropertiesParser

from l20n.migrate.util import parse, ftl_message_to_json
from l20n.migrate.transforms import evaluate, COPY, PLURALS, REPLACE, SOURCE


class MockContext(unittest.TestCase):
    # Static categories corresponding to en-US.
    plural_categories = ('one', 'other')

    def get_source(self, path, key):
        return self.strings.get(key, None).get_val()


class TestPlural(MockContext):
    def setUp(self):
        self.strings = parse(PropertiesParser, '''
            deleteAll=Delete this download?;Delete all downloads?
        ''')

        self.message = FTL.Entity(
            FTL.Identifier('delete-all'),
            value=PLURALS(
                SOURCE(self.strings, 'deleteAll'),
                FTL.ExternalArgument('num'),
                lambda var: COPY(var)
            )
        )

    def test_plural(self):
        self.assertEqual(
            evaluate(self, self.message).toJSON(),
            ftl_message_to_json('''
                delete-all = { $num ->
                    [one] Delete this download?
                   *[other] Delete all downloads?
                }
            ''')
        )

    def test_plural_too_few_variants(self):
        self.plural_categories = ('one', 'few', 'many', 'other')
        self.assertEqual(
            evaluate(self, self.message).toJSON(),
            ftl_message_to_json('''
                delete-all = { $num ->
                    [one] Delete this download?
                   *[few] Delete all downloads?
                }
            ''')
        )

    def test_plural_too_many_variants(self):
        self.plural_categories = ('one',)
        self.assertEqual(
            evaluate(self, self.message).toJSON(),
            ftl_message_to_json('''
                delete-all = { $num ->
                   *[one] Delete this download?
                }
            ''')
        )


class TestPluralReplace(MockContext):
    def setUp(self):
        self.strings = parse(PropertiesParser, '''
            deleteAll=Delete this download?;Delete #1 downloads?
        ''')

    def test_plural_replace(self):
        msg = FTL.Entity(
            FTL.Identifier('delete-all'),
            value=PLURALS(
                SOURCE(self.strings, 'deleteAll'),
                FTL.ExternalArgument('num'),
                lambda var: REPLACE(
                    var,
                    {'#1': [FTL.ExternalArgument('num')]}
                )
            )
        )

        self.assertEqual(
            evaluate(self, msg).toJSON(),
            ftl_message_to_json('''
                delete-all = { $num ->
                    [one] Delete this download?
                   *[other] Delete { $num } downloads?
                }
            ''')
        )


if __name__ == '__main__':
    unittest.main()
