#!/usr/bin/python
import json
from pandocfilters import walk
from unicodedata import east_asian_width


def pandoc_json(fp):
    doc = json.load(fp)
    if 'meta' in doc:
        meta = doc['meta']
    elif doc[0]:  # old API
        meta = doc[0]['unMeta']
    else:
        meta = {}
    return meta, doc


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


prev_str = None
prev_softbreak = False
softbreak = {'t': 'SoftBreak'}


def handle_wiki_link(key, value):
    if key == 'Link':
        value[2] = [
            '/' + s[5:] if s.startswith('wiki:') else s for s in value[2]
        ]
        return True
    return False


def handle_east_asian_line_break(key, value):
    global prev_str
    global prev_softbreak
    if key == 'Plain' or key == 'Para':
        prev_str = None
    elif key == 'Str':
        res = None
        if not (prev_softbreak and east_asian_str_edge(prev_str, False) and
                east_asian_str_edge(value, True)):
            # Not our SoftBreak to remove
            if prev_softbreak:
                res = [softbreak, {'t': 'Str', 'c': value}]
        prev_str = value
        prev_softbreak = False
        return res
    elif key == 'SoftBreak':
        prev_softbreak = True
        # Remove SoftBreak by default
        # SoftBreak must occur when no new Plain or Para is seen
        return []


def wiki_action(key, value, *_):
    if not handle_wiki_link(key, value):
        return handle_east_asian_line_break(key, value)


def gen_summary(doc, lim_blocks=2):
    summary = {k:v for k,v in doc.items() if k != 'blocks'}
    blks = doc.get('blocks')
    if blks:
        summary['blocks'] = blks[:lim_blocks]
    return summary


def transform(doc, meta, actions):
    altered = doc
    for action in actions:
        altered = walk(altered, action, format, meta)
    return altered
