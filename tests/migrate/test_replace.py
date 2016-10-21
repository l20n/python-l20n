# coding=utf8

import unittest

import l20n.format.ast as FTL
from compare_locales.parser import PropertiesParser

from l20n.migrate.util import parse, ftl_message_to_json
from l20n.migrate.transforms import evaluate, REPLACE, SOURCE


class MockContext(unittest.TestCase):
    def get_source(self, path, key):
        return self.strings.get(key, None).get_val()


class TestReplace(MockContext):
    def setUp(self):
        self.strings = parse(PropertiesParser, '''
            hello = Hello, #1!
            welcome = Welcome, #1, to #2!
            first = #1 Bar
            last = Foo #1
        ''')

    def test_replace_one(self):
        msg = FTL.Entity(
            FTL.Identifier(u'hello'),
            value=REPLACE(
                SOURCE(self.strings, 'hello'),
                {'#1': [FTL.ExternalArgument(u'username')]}
            )
        )

        self.assertEqual(
            evaluate(self, msg).toJSON(),
            ftl_message_to_json('''
                hello = Hello, { $username }!
            ''')
        )

    def test_replace_two(self):
        msg = FTL.Entity(
            FTL.Identifier(u'welcome'),
            value=REPLACE(
                SOURCE(self.strings, 'welcome'),
                {'#1': [FTL.ExternalArgument(u'username')],
                 '#2': [FTL.ExternalArgument(u'appname')]}
            )
        )

        self.assertEqual(
            evaluate(self, msg).toJSON(),
            ftl_message_to_json('''
                welcome = Welcome, { $username }, to { $appname }!
            ''')
        )

    def test_replace_too_many(self):
        msg = FTL.Entity(
            FTL.Identifier(u'welcome'),
            value=REPLACE(
                SOURCE(self.strings, 'welcome'),
                {'#1': [FTL.ExternalArgument(u'username')],
                 '#2': [FTL.ExternalArgument(u'appname')],
                 '#3': [FTL.ExternalArgument(u'extraname')]}
            )
        )

        self.assertEqual(
            evaluate(self, msg).toJSON(),
            ftl_message_to_json('''
                welcome = Welcome, { $username }, to { $appname }!
            ''')
        )

    def test_replace_too_few(self):
        msg = FTL.Entity(
            FTL.Identifier(u'welcome'),
            value=REPLACE(
                SOURCE(self.strings, 'welcome'),
                {'#1': [FTL.ExternalArgument(u'username')]}
            )
        )

        self.assertEqual(
            evaluate(self, msg).toJSON(),
            ftl_message_to_json('''
                welcome = Welcome, { $username }, to #2!
            ''')
        )

    def test_replace_first(self):
        msg = FTL.Entity(
            FTL.Identifier(u'first'),
            value=REPLACE(
                SOURCE(self.strings, 'first'),
                {'#1': [FTL.ExternalArgument(u'foo')]}
            )
        )

        self.assertEqual(
            evaluate(self, msg).toJSON(),
            ftl_message_to_json('''
                first = { $foo } Bar
            ''')
        )

    def test_replace_last(self):
        msg = FTL.Entity(
            FTL.Identifier(u'last'),
            value=REPLACE(
                SOURCE(self.strings, 'last'),
                {'#1': [FTL.ExternalArgument(u'bar')]}
            )
        )

        self.assertEqual(
            evaluate(self, msg).toJSON(),
            ftl_message_to_json('''
                last = Foo { $bar }
            ''')
        )


if __name__ == '__main__':
    unittest.main()
