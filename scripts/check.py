# -*- coding: utf-8 -*-
"""Validate the generated public artifact, including editable CMS content."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import os
from xml.etree import ElementTree
import re
import json
from content import load_articles, public_articles, STATIC_PAGES

SOURCE=Path(__file__).resolve().parents[1]
ROOT=Path(os.environ.get('SITE_OUTPUT',str(SOURCE))).resolve()
posts=load_articles(SOURCE/'articles.json')
public=public_articles(posts)

class Page(HTMLParser):
    def __init__(self,text):
        super().__init__();self.links=[];self.ids=set();self.h1=0;self.feed(text)
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:
            assert attrs['id'] not in self.ids,'Duplicate anchor: '+attrs['id']
            self.ids.add(attrs['id'])
        if tag=='h1':self.h1+=1
        if tag in ('a','img','script','link'):
            url=attrs.get('href',attrs.get('src'))
            if url is not None:self.links.append(url)
        if tag=='img':assert 'alt' in attrs,'Images need an alt field'

files=list(ROOT.glob('*.html'))
assert {p.name for p in files}==set(STATIC_PAGES)|{p['slug'] for p in public},'Unexpected/missing generated pages; use scripts/publish.py for a clean build'
for file in files:
    text=file.read_text(encoding='utf-8');page=Page(text)
    assert page.h1==1,(file.name,'h1 count')
    assert 'class="reading-time"' not in text,(file.name,'reading duration')
    assert '<meta name="description"' in text and '<link rel="canonical"' in text,file.name
    for url in page.links:
        assert url and url!='#',(file.name,'empty link')
        parts=urlsplit(url)
        if parts.scheme or parts.netloc:continue
        target=ROOT/unquote(parts.path.lstrip('/')) if parts.path else file
        assert target.is_file(),(file.name,url,'missing local target')
        if parts.fragment:
            assert unquote(parts.fragment) in Page(target.read_text(encoding='utf-8')).ids,(file.name,url,'missing fragment')
    schema=re.search(r'<script type="application/ld\+json">(.*?)</script>',text,re.S)
    assert schema,file.name
    json.loads(schema.group(1))
for post in public:
    text=(ROOT/post['slug']).read_text(encoding='utf-8')
    assert f'datetime="{post["datePublished"]}"' in text,post['slug']
    assert '<span class="badge">待确认草稿</span>' not in text,post['slug']
sitemap_paths={urlsplit(e.text).path.lstrip('/') for e in ElementTree.parse(ROOT/'sitemap.xml').iter() if e.tag.endswith('}loc') and e.text}
for post in posts:
    if post['draft']:
        assert not (ROOT/post['slug']).exists(),(post['slug'],'draft page must not be public')
        assert post['slug'] not in sitemap_paths,(post['slug'],'draft in sitemap')
assert (ROOT/'CNAME').read_bytes()==(SOURCE/'CNAME').read_bytes()
assert (ROOT/'assets/telegram.jpg').read_bytes()==(SOURCE/'assets/telegram.jpg').read_bytes()
print(f'PASS: {len(files)} public pages, dates, schema, links, anchors and draft exclusion.')
