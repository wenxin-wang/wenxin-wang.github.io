#!/usr/bin/python
from pandocfilters import toJSONFilter
from unicodedata import east_asian_width


def change_meta(meta):
    meta['wiki'] = {
        't': 'MetaList',
        'c': [{
            't': 'MetaString',
            'c': s
        } for s in meta['wiki']['c'].split()]
    }


def east_asian_str_edge(s, left):
    s = s[0 if left else -1]
    res = east_asian_width(s)
    return res == 'W' or res == 'F'


changed_meta = False
prev_str = None
prev_softbreak = False
softbreak = {'t': 'SoftBreak'}


def wiki(key, value, _, meta):
    global changed_meta
    global prev_str
    global prev_softbreak
    if 'wiki' in meta and not changed_meta:
        changed_meta = True
        change_meta(meta)
    if key == 'Link':
        value[2] = [
            '/' + s[5:] if s.startswith('wiki:') else s for s in value[2]
        ]
    elif key == 'Plain' or key == 'Para':
        prev_str = None
    elif key == 'Str':
        res = None
        if not (prev_softbreak and east_asian_str_edge(prev_str, False) and
                east_asian_str_edge(value, True)):
            # Not our SoftBreak to remove
            res = [softbreak, {'t': 'Str', 'c': value}]
        prev_str = value
        prev_softbreak = False
        return res
    elif key == 'SoftBreak':
        prev_softbreak = True
        # Remove SoftBreak by default
        # SoftBreak must occur when no new Plain or Para is seen
        return []


if __name__ == "__main__":
    toJSONFilter(wiki)
