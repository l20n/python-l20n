# coding=utf8

import time


def by_first_commit(a, b):
    """Order two changesets by their first commit date."""
    return int(a['first_commit'] - b['first_commit'])


def convert_blame_to_changesets(blame_json):
    """Convert a blame dict into a list of changesets.

    The blame information in `blame_json` should be a dict of the following
    structure:

        {
            'authors': [
                'A.N. Author <author@example.com>',
            ],
            'blame': {
                'path/one': {
                    'key1': [0, 1346095921.0],
                },
            }
        }

    It will be transformed into a list of changesets which can be fed into
    `MergeContext.serialize_changeset`:

        [
            {
                'author': 'A.N. Author <author@example.com>',
                'first_commit': 1346095921.0,
                'changes': {
                    ('path/one', 'key1'),
                }
            },
        ]

    """
    now = time.time()
    changesets = [
        {
            'author': author,
            'first_commit': now,
            'changes': set()
        } for author in blame_json['authors']
    ]

    for path, keys_info in blame_json['blame'].iteritems():
        for key, (author_index, timestamp) in keys_info.iteritems():
            changeset = changesets[author_index]
            changeset['changes'].add((path, key))
            if timestamp < changeset['first_commit']:
                changeset['first_commit'] = timestamp

    return sorted(changesets, by_first_commit)
