#!/usr/bin/env python

from lxml import html, etree
import requests
import csv
import io
import sys

baseurl = 'https://docs.python.org/3.6/library/'
pages = [
    {
        'label': 'Python builtin constant',
         'url': baseurl + 'constants.html',
         'xpath': '//dl',
    },
    {
        'label': 'Python builtin function',
         'url': baseurl + 'functions.html',
         'xpath': '//dl',
    },
    {
        'label': 'Python special attribute',
         'url': baseurl + 'stdtypes.html',
         'xpath': '//div[@id="special-attributes"]/dl',
    },
    {
        'label': 'Python <code>str</code> method',
         'url': baseurl + 'stdtypes.html',
         'xpath': '//div[@id="string-methods"]/dl',
    },
    {
        'label': 'Python <code>set</code> operation',
         'url': baseurl + 'stdtypes.html',
         'xpath': '//div[@id="set-types-set-frozenset"]/dl/dd/dl',
    },
    {
        'label': 'Python builtin exception',
         'url': baseurl + 'exceptions.html',
         'xpath': '//div/dl',
    },
    {
        'label': 'Python <code>string</code> prop',
         'url': baseurl + 'string.html',
         'xpath': '//div[@id="string-constants"]/dl',
    },
    {
        'label': 'Python <code>re</code> prop',
         'url': baseurl + 're.html',
         'xpath': '//div[@id="module-contents"]/dl',
    },
    {
        'label': 'Python <code>datetime</code> prop',
         'url': baseurl + 'datetime.html',
         'xpath': '//dl',
    },
    ]
classes = [ # Only collect these types of data as specified in DL tag class.
    'data', 'function', 'class', 'attribute', 'method', 'staticmethod', 'describe',
    'exception', 'classmethod',
    ]


def main(args):
    results = []
    for page in pages:
        extract(results, **page)
    output = generate_csv(results)
    print(output)


def replace_links(tree):
    """Replace anchors with their text."""
    for a in tree.xpath('.//a'):
        for e in a.iterchildren():
            a.addprevious(e)
    etree.strip_elements(tree, 'a', with_tail=False)


def tostring(e_iter, method='html'):
    if type(e_iter) == html.HtmlElement:
        return etree.tostring(e_iter, encoding='unicode', method=method).strip()
    if type(e_iter) == str:
        return e_iter
    return ''.join([tostring(e) for e in e_iter])


def node(tree, xpath, default=''):
    nodes = tree.xpath(xpath)
    return nodes[0] if nodes else default


def extract(results, label, url, xpath):
    """Populate results by scraping url>xpath"""
    tree = html.fromstring(requests.get(url).content)
    replace_links(tree)
    for dl in tree.xpath(xpath):
        if sum(1 for v in dl.values() if v not in classes) > 0:
            continue # Skip DL tags of unknown types (usually have empty DD tags).
        dd = node(dl, './dd')
        back_e = node(dd, './p[1]|./blockquote/div/p[1]|./blockquote/div[1]')
        if not back_e: continue # Skip items with no description.
        back = tostring(back_e)
        back_e.drop_tree() # Remove used part so not repeated in other.
        other = tostring(dd.iterchildren())
        for dt in dl.xpath('./dt'):
            # This could be more straightfoward. First, extract contents of sig.
            opts_e = dt.xpath('.//{0}[1]/{1}{0}[1]/{2}node()[{2}{0}]'.format(
                'span[@class="sig-paren"]',
                'following-sibling::',
                'preceding-sibling::',
                ))
            opts = tostring(opts_e)
            # Recover parentheses for empty signatures (simple methods).
            if dt.xpath('.//span[@class="sig-paren"]') and not opts: opts = '()'
            opts = '<em>' + opts + '</em>' if opts else opts
            opts_t = '({})'.format(tostring(opts_e, 'text')) if opts else ''
            dt_prop = node(dt, './/em[@class="property"]/text()')
            dt_class = node(dt, './/code[@class="descclassname"]/text()')
            dt_name = node(dt, './/code[@class="descname"]/text()')
            back = back.replace(dt_name, '<strike>'+dt_name+'</strike>')
            front = dt_class + dt_name + opts_t
            altfront = '<code>{}{}</code>'.format(dt_name, '()' if opts else '')
            if dt_class:
                lbl = 'Python <code>' + dt_class.strip('.') + '</code> prop'
            else:
                lbl = label
            if opts:
                other = '<p>{}<code>{}{}</code></p>{}'.format(
                    dt_prop, front, opts, other)
            results += [[
                front, lbl, back, None, other, 'reverse', altfront, url, 'python'
                ]]


def generate_csv(rows):
    """Generate final output as CSV."""
    try:
        # This supposedly only works in 3.X but works in my 2.7.13.
        output = io.StringIO()
        csv.writer(output).writerows(rows)
    except:  # Should be fast enough we can forgo key/sysexit
        # May get here on 2.X; then need to use io.BytesIO.
        # Ideally test old versions and determine exact exception.
        output = io.BytesIO()
        csv.writer(output).writerows(rows)
    return output.getvalue()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

