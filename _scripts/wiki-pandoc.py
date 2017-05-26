#!/usr/bin/python

from pandocfilters import toJSONFilter

changed_meta = False


def change_meta(meta):
    meta['wiki'] = {
        't': 'MetaList',
        'c': [{
            't': 'MetaString',
            'c': s
        } for s in meta['wiki']['c'].split()]
    }


def wiki(key, value, _, meta):
    global changed_meta
    if 'wiki' in meta and not changed_meta:
        changed_meta = True
        change_meta(meta)
    if key == 'Link':
        value[2] = [
            '/' + s[5:] if s.startswith('wiki:') else s for s in value[2]
        ]


if __name__ == "__main__":
    toJSONFilter(wiki)
