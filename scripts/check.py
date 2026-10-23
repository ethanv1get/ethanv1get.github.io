"""Check links, page semantics and preservation against the original Git baseline."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import re,subprocess,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
BASELINE='f6c3ce62051bfaa328ab8d9e18a9dda4c6742593'
class Page(HTMLParser):
    def __init__(self,text):
        super().__init__();self.links=[];self.ids=set();self.h1=0;self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.add(a['id'])
        if tag=='h1':self.h1+=1
        if tag in ['a','img','script','link']:
            u=a.get('href',a.get('src'))
            if u is not None:self.links.append(u)
        if tag=='img':assert 'alt' in a,'Missing alt text'
files=list(ROOT.glob('*.html'))
for file in files:
    text=file.read_text();page=Page(text)
    assert page.h1==1,(file.name,'h1 count')
    assert '孙译' not in text,file.name
    assert '<meta name="description"' in text and '<link rel="canonical"' in text
    for url in page.links:
        assert url and url!='#',(file.name,'empty link')
        parts=urlsplit(url)
        if parts.scheme or parts.netloc:continue
        path=ROOT/unquote(parts.path.lstrip('/')) if parts.path else file
        assert path.is_file(),(file.name,url)
        if parts.fragment:
            assert unquote(parts.fragment) in Page(path.read_text()).ids,(file.name,url,'missing fragment')
if (ROOT/'.git').exists():
    original=subprocess.check_output(['git','show',BASELINE+':hello.html'],cwd=ROOT,text=True)
    body=re.search(r'<h2>保持好奇</h2>(.*?)<a class="back"',original,re.S).group(0).split('<a class="back"')[0]
    # Ignore IDs added for in-page navigation, preserve every original heading and paragraph.
    actual=(ROOT/'hello.html').read_text()
    actual=re.sub(r' id="(?:curiosity|ideas|record)"','',actual)
    assert body in actual,'Original article changed'
    original_qr=subprocess.check_output(['git','show',BASELINE+':assets/telegram.jpg'],cwd=ROOT)
    assert hashlib.sha256(original_qr).digest()==hashlib.sha256((ROOT/'assets/telegram.jpg').read_bytes()).digest()
    assert (ROOT/'CNAME').read_bytes()==subprocess.check_output(['git','show',BASELINE+':CNAME'],cwd=ROOT)
else:
    print('NOTE: No Git history; baseline preservation comparison skipped.')
assert len(json.loads((ROOT/'articles.json').read_text()))==1
print(f'PASS: {len(files)} pages, local links/assets/fragments, metadata, original article, QR and domain preserved.')
