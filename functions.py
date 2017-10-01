#!/usr/bin/env python

from pyquery import PyQuery as pq
import urllib

import re
from xml.etree.ElementTree import tostring
import csv
import io
url = 'https://docs.python.org/3.6/library/functions.html'
d = pq(url=url)
# d = pq(url=your_url, opener=lambda url, **kw: urlopen(url).read())

rows = []
sig_p = re.compile('<span class="sig-paren">\(</span>(.*)<span class="sig-paren">\)</span>')

for e in d('dl'):
    try:
        sig = '({})'.format(sig_p.search(tostring(e.find('dt')).decode('utf-8')).group(1))
    except AttributeError:
        sig = None
    name = e.find('dt').find('code').text
    desc_node = e.find('dd').find('p')
    if desc_node == None:
        desc_node = e.find('dd').find('blockquote').find('div')
    #print(repr(desc_node))
    #print(dir(desc_node))
    desc = tostring(desc_node).decode('utf-8')
    if desc.endswith('</p>') and desc[0:3] == '<p>':
        desc = desc[3:-4]
    try:
        e.find('dd').remove(desc_node)
        rest = tostring(e.find('dd')).decode('utf-8')
        rest = rest.replace('<dd>','')
        rest = rest.replace('</dd>','')
    except:
        rest = None

    rows += [[
        '<code>{}</code>'.format(name),
        'Python builtin function',
        desc,
        'description',
        '<p>{}</p>{}'.format(
            '<code>{}{}</code>'.format(name, ' <em>{}</em>'.format(sig) if sig else sig),
            rest,
        ),
        'Reverse',
        None,
        url,
        'python'
    ]]

output = io.StringIO()
csv.writer(output).writerows(rows)
print(output.getvalue())

#for i in range(len(d('dl'))):
    
#    print(d('dl').eq(i).find('dt').text())

