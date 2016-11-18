# coding=utf8

import pkgutil
import json


def in_canonical_order(a, b):
    return canonical_order.index(a) - canonical_order.index(b)


cldr_plurals = json.loads(
    pkgutil.get_data('l20n.migrate', 'cldr_data/plurals.json')
)

rules = cldr_plurals['supplemental']['plurals-type-cardinal']
canonical_order = ('zero', 'one', 'two', 'few', 'many', 'other')

categories = {}
for lang, rules in rules.items():
    categories[lang] = tuple(sorted(map(
        lambda key: key.replace('pluralRule-count-', ''),
        rules.keys()
    ), in_canonical_order))


def get_plural_categories(lang):
    langs_categories = categories.get(lang, None)

    if langs_categories is None:
        raise RuntimeError('Unknown language: {}'.format(lang))

    return langs_categories
