# coding=utf8

import unittest

import l20n.format.ast as FTL
from compare_locales.parser import PropertiesParser, DTDParser

from l20n.migrate.util import parse, ftl_message_to_json
from l20n.migrate.transforms import evaluate, COPY, SOURCE


class MockContext(unittest.TestCase):
    def get_source(self, path, key):
        return self.strings.get(key, None).get_val()


class TestCopy(MockContext):
    def setUp(self):
        self.strings = parse(PropertiesParser, '''
            foo = Foo
            foo.unicode.middle = Foo\\u0020Bar
            foo.unicode.begin = \\u0020Foo
            foo.unicode.end = Foo\\u0020

            foo.html.entity = &lt;&#x21E7;&#x2318;K&gt;
        ''')

    def test_copy(self):
        msg = FTL.Entity(
            FTL.Identifier('foo'),
            value=COPY(
                SOURCE(self.strings, 'foo')
            )
        )

        self.assertEqual(
            evaluate(self, msg).toJSON(),
            ftl_message_to_json('''
                foo = Foo
            ''')
        )

    def test_copy_escape_unicode_middle(self):
        msg = FTL.Entity(
            FTL.Identifier('foo-unicode-middle'),
            value=COPY(
                SOURCE(self.strings, 'foo.unicode.middle')
            )
        )

        self.assertEqual(
            evaluate(self, msg).toJSON(),
            ftl_message_to_json('''
                foo-unicode-middle = Foo Bar
            ''')
        )

    def test_copy_escape_unicode_begin(self):
        msg = FTL.Entity(
            FTL.Identifier('foo-unicode-begin'),
            value=COPY(
                SOURCE(self.strings, 'foo.unicode.begin')
            )
        )

        self.assertEqual(
            evaluate(self, msg).toJSON(),
            ftl_message_to_json('''
                foo-unicode-begin = " Foo"
            ''')
        )

    def test_copy_escape_unicode_end(self):
        msg = FTL.Entity(
            FTL.Identifier('foo-unicode-end'),
            value=COPY(
                SOURCE(self.strings, 'foo.unicode.end')
            )
        )

        self.assertEqual(
            evaluate(self, msg).toJSON(),
            ftl_message_to_json('''
                foo-unicode-end = "Foo "
            ''')
        )

    def test_copy_html_entity(self):
        msg = FTL.Entity(
            FTL.Identifier('foo-html-entity'),
            value=COPY(
                SOURCE(self.strings, 'foo.html.entity')
            )
        )

        self.assertEqual(
            evaluate(self, msg).toJSON(),
            ftl_message_to_json('''
                foo-html-entity = &lt;&#x21E7;&#x2318;K&gt;
            ''')
        )


class TestCopyTraits(MockContext):
    def setUp(self):
        self.strings = parse(DTDParser, '''
            <!ENTITY checkForUpdatesButton.label       "Check for updates">
            <!ENTITY checkForUpdatesButton.accesskey   "C">
        ''')

    def test_copy_accesskey(self):
        msg = FTL.Entity(
            FTL.Identifier('check-for-updates'),
            traits=[
                FTL.Member(
                    FTL.Keyword('label', 'xul'),
                    COPY(
                        SOURCE(self.strings, 'checkForUpdatesButton.label')
                    )
                ),
                FTL.Member(
                    FTL.Keyword('accesskey', 'xul'),
                    COPY(
                        SOURCE(self.strings, 'checkForUpdatesButton.accesskey')
                    )
                ),
            ]
        )

        self.assertEqual(
            evaluate(self, msg).toJSON(),
            ftl_message_to_json('''
                check-for-updates =
                  [xul/label] Check for updates
                  [xul/accesskey] C
            ''')
        )


if __name__ == '__main__':
    unittest.main()
