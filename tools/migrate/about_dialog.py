# coding=utf8

import l20n.format.ast as FTL
from l20n.migrate import CONCAT, COPY, EXTERNAL, REPLACE, SOURCE


def migrate(ctx):
    """Migrate about:dialog, part {index}"""

    ctx.add_reference('browser/aboutDialog.ftl', realpath='aboutDialog.ftl')
    ctx.add_localization('browser/chrome/browser/aboutDialog.dtd')

    ctx.add_transforms('browser/aboutDialog.ftl', [
        FTL.Entity(
            id=FTL.Identifier('update-failed'),
            value=CONCAT(
                COPY(
                    SOURCE(
                        'browser/chrome/browser/aboutDialog.dtd',
                        'update.failed.start'
                    )
                ),
                COPY('<a>'),
                COPY(
                    SOURCE(
                        'browser/chrome/browser/aboutDialog.dtd',
                        'update.failed.linkText'
                    )
                ),
                COPY('</a>'),
                COPY(
                    SOURCE(
                        'browser/chrome/browser/aboutDialog.dtd',
                        'update.failed.end'
                    )
                )
            )
        ),
        FTL.Entity(
            id=FTL.Identifier('channel-desc'),
            value=CONCAT(
                COPY(
                    SOURCE(
                        'browser/chrome/browser/aboutDialog.dtd',
                        'channel.description.start'
                    )
                ),
                EXTERNAL('channelname'),
                COPY(
                    SOURCE(
                        'browser/chrome/browser/aboutDialog.dtd',
                        'channel.description.end'
                    )
                )
            )
        ),
        FTL.Entity(
            id=FTL.Identifier('community'),
            value=CONCAT(
                REPLACE(
                    SOURCE(
                        'browser/chrome/browser/aboutDialog.dtd',
                        'community.start2'
                    ),
                    {
                        '&brandShortName;': [
                            FTL.ExternalArgument('brand-short-name')
                        ]
                    }
                ),
                COPY('<a>'),
                REPLACE(
                    SOURCE(
                        'browser/chrome/browser/aboutDialog.dtd',
                        'community.mozillaLink'
                    ),
                    {
                        '&vendorShortName;': [
                            FTL.ExternalArgument('vendor-short-name')
                        ]
                    }
                ),
                COPY('</a>'),
                COPY(
                    SOURCE(
                        'browser/chrome/browser/aboutDialog.dtd',
                        'community.middle2'
                    )
                ),
                COPY('<a>'),
                COPY(
                    SOURCE(
                        'browser/chrome/browser/aboutDialog.dtd',
                        'community.creditsLink'
                    )
                ),
                COPY('</a>'),
                COPY(
                    SOURCE(
                        'browser/chrome/browser/aboutDialog.dtd',
                        'community.end3'
                    )
                )
            )
        ),
    ])
