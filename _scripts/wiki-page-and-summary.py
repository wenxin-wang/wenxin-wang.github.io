#!/usr/bin/python
import io
import sys
import json
import subprocess
import wiki_pandoc as wiki


def json_to_pandoc(doc, filename, args):
    with open(filename, 'w') as fd:
        page_writer = subprocess.Popen(['pandoc'] + args + ['-o', filename],
                                       encoding='utf8', stdin=subprocess.PIPE,
                                       stdout=fd)
        json.dump(doc, page_writer.stdin)
        page_writer.stdin.close()
        page_writer.wait()


def main():
    page_org = sys.argv[1]
    page_html = sys.argv[2]
    page_template = sys.argv[3]
    summary_html = sys.argv[4]
    page_reader = subprocess.Popen(['pandoc', '-s', '-t', 'json', page_org],
                                   stdout=subprocess.PIPE)
    meta, doc = wiki.pandoc_json(page_reader.stdout)
    # Do we have to wait here?
    wiki.change_meta(meta)
    full = wiki.transform(doc, meta, [wiki.wiki_action])
    summary = wiki.gen_summary(doc)
    print('full')
    json_to_pandoc(full, page_html, ['-s', '-f', 'json', '--template',
                                     page_template])
    print('summary')
    json_to_pandoc(summary, summary_html, ['-f', 'json', '-t', 'html'])

if __name__ == "__main__":
    main()
