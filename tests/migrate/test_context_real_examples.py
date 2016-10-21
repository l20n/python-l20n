# coding=utf8

import os
import unittest

import l20n.format.ast as FTL

from l20n.migrate.util import ftl_resource_to_json, to_json
from l20n.migrate.context import MergeContext
from l20n.migrate.transforms import (
    CONCAT, COPY, EXTERNAL, PLURALS, REPLACE, SOURCE
)


def here(*parts):
    dirname = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dirname, *parts)


class TestMergeAboutDownloads(unittest.TestCase):
    def setUp(self):
        self.ctx = MergeContext(
            lang='pl',
            reference_dir=here('fixtures/en-US'),
            localization_dir=here('fixtures/pl')
        )

        self.ctx.add_reference('aboutDownloads.ftl')
        self.ctx.add_localization('aboutDownloads.dtd')
        self.ctx.add_localization('aboutDownloads.properties')

        self.ctx.add_transforms('aboutDownloads.ftl', [
            FTL.Entity(
                id=FTL.Identifier('title'),
                value=COPY(
                    SOURCE(
                        'aboutDownloads.dtd',
                        'aboutDownloads.title'
                    )
                )
            ),
            FTL.Entity(
                id=FTL.Identifier('header'),
                value=COPY(
                    SOURCE(
                        'aboutDownloads.dtd',
                        'aboutDownloads.header'
                    )
                )
            ),
            FTL.Entity(
                id=FTL.Identifier('empty'),
                value=COPY(
                    SOURCE(
                        'aboutDownloads.dtd',
                        'aboutDownloads.empty'
                    )
                )
            ),
            FTL.Entity(
                id=FTL.Identifier('open-menuitem'),
                traits=[
                    FTL.Member(
                        FTL.Keyword('label', 'html'),
                        COPY(
                            SOURCE(
                                'aboutDownloads.dtd',
                                'aboutDownloads.open'
                            )
                        )
                    )
                ]
            ),
            FTL.Entity(
                id=FTL.Identifier('retry-menuitem'),
                traits=[
                    FTL.Member(
                        FTL.Keyword('label', 'html'),
                        COPY(
                            SOURCE(
                                'aboutDownloads.dtd',
                                'aboutDownloads.retry'
                            )
                        )
                    )
                ]
            ),
            FTL.Entity(
                id=FTL.Identifier('remove-menuitem'),
                traits=[
                    FTL.Member(
                        FTL.Keyword('label', 'html'),
                        COPY(
                            SOURCE(
                                'aboutDownloads.dtd',
                                'aboutDownloads.remove'
                            )
                        )
                    )
                ]
            ),
            FTL.Entity(
                id=FTL.Identifier('pause-menuitem'),
                traits=[
                    FTL.Member(
                        FTL.Keyword('label', 'html'),
                        COPY(
                            SOURCE(
                                'aboutDownloads.dtd',
                                'aboutDownloads.pause'
                            )
                        )
                    )
                ]
            ),
            FTL.Entity(
                id=FTL.Identifier('resume-menuitem'),
                traits=[
                    FTL.Member(
                        FTL.Keyword('label', 'html'),
                        COPY(
                            SOURCE(
                                'aboutDownloads.dtd',
                                'aboutDownloads.resume'
                            )
                        )
                    )
                ]
            ),
            FTL.Entity(
                id=FTL.Identifier('cancel-menuitem'),
                traits=[
                    FTL.Member(
                        FTL.Keyword('label', 'html'),
                        COPY(
                            SOURCE(
                                'aboutDownloads.dtd',
                                'aboutDownloads.cancel'
                            )
                        )
                    )
                ]
            ),
            FTL.Entity(
                id=FTL.Identifier('remove-all-menuitem'),
                traits=[
                    FTL.Member(
                        FTL.Keyword('label', 'html'),
                        COPY(
                            SOURCE(
                                'aboutDownloads.dtd',
                                'aboutDownloads.removeAll'
                            )
                        )
                    )
                ]
            ),
            FTL.Entity(
                id=FTL.Identifier('delete-all-title'),
                value=COPY(
                    SOURCE(
                        'aboutDownloads.properties',
                        'downloadAction.deleteAll'
                    )
                )
            ),
            FTL.Entity(
                id=FTL.Identifier('delete-all-message'),
                value=PLURALS(
                    SOURCE(
                        'aboutDownloads.properties',
                        'downloadMessage.deleteAll'
                    ),
                    FTL.ExternalArgument('num'),
                    lambda var: REPLACE(
                        var,
                        {'#1': [FTL.ExternalArgument('num')]}
                    )
                )
            ),
            FTL.Entity(
                id=FTL.Identifier('download-state-downloading'),
                value=COPY(
                    SOURCE(
                        'aboutDownloads.properties',
                        'downloadState.downloading'
                    )
                )
            ),
            FTL.Entity(
                id=FTL.Identifier('download-state-canceled'),
                value=COPY(
                    SOURCE(
                        'aboutDownloads.properties',
                        'downloadState.canceled'
                    )
                )
            ),
            FTL.Entity(
                id=FTL.Identifier('download-state-failed'),
                value=COPY(
                    SOURCE(
                        'aboutDownloads.properties',
                        'downloadState.failed'
                    )
                )
            ),
            FTL.Entity(
                id=FTL.Identifier('download-state-paused'),
                value=COPY(
                    SOURCE(
                        'aboutDownloads.properties',
                        'downloadState.paused'
                    )
                )
            ),
            FTL.Entity(
                id=FTL.Identifier('download-state-starting'),
                value=COPY(
                    SOURCE(
                        'aboutDownloads.properties',
                        'downloadState.starting'
                    )
                )
            ),
            FTL.Entity(
                id=FTL.Identifier('download-size-unknown'),
                value=COPY(
                    SOURCE(
                        'aboutDownloads.properties',
                        'downloadState.unknownSize'
                    )
                )
            ),
        ])

    def test_merge_context_all_messages(self):
        expected = {
            'aboutDownloads.ftl': ftl_resource_to_json('''
        # This Source Code Form is subject to the terms of the Mozilla Public
        # License, v. 2.0. If a copy of the MPL was not distributed with this
        # file, You can obtain one at http://mozilla.org/MPL/2.0/.

        title  = Pobrane pliki
        header = Twoje pobrane pliki
        empty  = Brak pobranych plików

        open-menuitem =
            [html/label] Otwórz
        retry-menuitem =
            [html/label] Spróbuj ponownie
        remove-menuitem =
            [html/label] Usuń
        pause-menuitem =
            [html/label] Wstrzymaj
        resume-menuitem =
            [html/label] Wznów
        cancel-menuitem =
            [html/label] Anuluj
        remove-all-menuitem =
            [html/label] Usuń wszystko

        delete-all-title   = Usuń wszystko
        delete-all-message = { $num ->
            [one] Usunąć pobrany plik?
            [few] Usunąć { $num } pobrane pliki?
           *[many] Usunąć { $num } pobranych plików?
        }

        download-state-downloading = Pobieranie…
        download-state-canceled    = Anulowane
        download-state-failed      = Nieudane
        download-state-paused      = Wstrzymane
        download-state-starting    = Rozpoczynanie…
        download-size-unknown      = Nieznany rozmiar
            ''')
        }

        self.assertDictEqual(
            to_json(self.ctx.merge_changeset()),
            expected
        )

    def test_merge_context_some_messages(self):
        changeset = {
            ('aboutDownloads.dtd', 'aboutDownloads.title'),
            ('aboutDownloads.dtd', 'aboutDownloads.header'),
            ('aboutDownloads.properties', 'downloadState.downloading'),
            ('aboutDownloads.properties', 'downloadState.canceled'),
        }

        expected = {
            'aboutDownloads.ftl': ftl_resource_to_json('''
        # This Source Code Form is subject to the terms of the Mozilla Public
        # License, v. 2.0. If a copy of the MPL was not distributed with this
        # file, You can obtain one at http://mozilla.org/MPL/2.0/.

        title                      = Pobrane pliki
        header                     = Twoje pobrane pliki
        download-state-downloading = Pobieranie…
        download-state-canceled    = Anulowane
            ''')
        }

        self.assertDictEqual(
            to_json(self.ctx.merge_changeset(changeset)),
            expected
        )


class TestMergeAboutDialog(unittest.TestCase):
    def setUp(self):
        self.ctx = MergeContext(
            lang='pl',
            reference_dir=here('fixtures/en-US'),
            localization_dir=here('fixtures/pl')
        )

        self.ctx.add_reference('aboutDialog.ftl')
        self.ctx.add_localization('aboutDialog.dtd')

        self.ctx.add_transforms('aboutDialog.ftl', [
            FTL.Entity(
                id=FTL.Identifier('update-failed'),
                value=CONCAT(
                    COPY(
                        SOURCE('aboutDialog.dtd', 'update.failed.start'),
                    ),
                    COPY('<a>'),
                    COPY(
                        SOURCE('aboutDialog.dtd', 'update.failed.linkText'),
                    ),
                    COPY('</a>'),
                    COPY(
                        SOURCE('aboutDialog.dtd', 'update.failed.end'),
                    ),
                )
            ),
            FTL.Entity(
                id=FTL.Identifier('channel-desc'),
                value=CONCAT(
                    COPY(
                        SOURCE('aboutDialog.dtd', 'channel.description.start'),
                    ),
                    EXTERNAL('channelname'),
                    COPY(
                        SOURCE('aboutDialog.dtd', 'channel.description.end'),
                    )
                )
            ),
            FTL.Entity(
                id=FTL.Identifier('community'),
                value=CONCAT(
                    REPLACE(
                        SOURCE('aboutDialog.dtd', 'community.start'),
                        {
                            '&brandShortName;': [
                                FTL.ExternalArgument('brand-short-name')
                            ]
                        }
                    ),
                    COPY('<a>'),
                    REPLACE(
                        SOURCE('aboutDialog.dtd', 'community.mozillaLink'),
                        {
                            '&vendorShortName;': [
                                FTL.ExternalArgument('vendor-short-name')
                            ]
                        }
                    ),
                    COPY('</a>'),
                    COPY(
                        SOURCE('aboutDialog.dtd', 'community.middle')
                    ),
                    COPY('<a>'),
                    COPY(
                        SOURCE('aboutDialog.dtd', 'community.creditsLink')
                    ),
                    COPY('</a>'),
                    COPY(
                        SOURCE('aboutDialog.dtd', 'community.end')
                    )
                )
            ),
        ])

    def test_merge_context_all_messages(self):
        expected = {
            'aboutDialog.ftl': ftl_resource_to_json('''
        # This Source Code Form is subject to the terms of the Mozilla Public
        # License, v. 2.0. If a copy of the MPL was not distributed with this
        # file, You can obtain one at http://mozilla.org/MPL/2.0/.

        update-failed = Aktualizacja się nie powiodła. <a>Pobierz</a>.
        channel-desc  = "Obecnie korzystasz z kanału { $channelname }. "
        community     = Program { $brand-short-name } został opracowany przez <a>organizację { $vendor-short-name }</a>, która jest <a>globalną społecznością</a>, starającą się zapewnić, by…
            ''')
        }

        self.assertDictEqual(
            to_json(self.ctx.merge_changeset()),
            expected
        )

    def test_merge_context_some_messages(self):
        changeset = {
            ('aboutDialog.dtd', 'update.failed.start'),
        }

        expected = {
            'aboutDialog.ftl': ftl_resource_to_json('''
        # This Source Code Form is subject to the terms of the Mozilla Public
        # License, v. 2.0. If a copy of the MPL was not distributed with this
        # file, You can obtain one at http://mozilla.org/MPL/2.0/.

        update-failed = Aktualizacja się nie powiodła. <a>Pobierz</a>.
            ''')
        }

        self.assertDictEqual(
            to_json(self.ctx.merge_changeset(changeset)),
            expected
        )
