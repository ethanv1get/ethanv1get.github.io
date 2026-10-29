# -*- coding: utf-8 -*-
"""Isolated publishing tests. No test articles are committed or deployed."""
from pathlib import Path
from tempfile import TemporaryDirectory
import base64
import json
import shutil
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]

class CmsPublishingTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory(prefix='cms-publish-test-',dir=ROOT.parent)
        self.root=Path(self.tmp.name)/'site'
        shutil.copytree(ROOT,self.root,ignore=shutil.ignore_patterns('.git','_site','__pycache__','node_modules'))
        self.original=(self.root/'articles.json').read_bytes()
        self.posts=json.loads(self.original)
    def tearDown(self):self.tmp.cleanup()
    def save(self):
        (self.root/'articles.json').write_text(json.dumps(self.posts,ensure_ascii=False),encoding='utf-8')
    def build(self,ok=True):
        p=subprocess.run([sys.executable,str(self.root/'scripts/publish.py')],capture_output=True,text=True)
        self.assertEqual(p.returncode==0,ok,p.stdout+p.stderr)
        return p
    def test_existing_content_and_design_are_preserved(self):
        self.build()
        self.assertEqual((self.root/'articles.json').read_bytes(),self.original)
        html=(self.root/'_site/hello.html').read_text()
        self.assertIn('发布于 2026年10月24日',html)
        self.assertIn('很多事情，都是从一个小小的疑问开始的。',html)
        self.assertEqual((self.root/'_site/style.css').read_bytes(),(ROOT/'style.css').read_bytes())
        self.assertEqual((self.root/'_site/assets/telegram.jpg').read_bytes(),(ROOT/'assets/telegram.jpg').read_bytes())
    def test_new_cms_article_category_image_and_dates(self):
        self.posts.append({'title':'包含 < & 的标题','slug':'new-note','datePublished':'2026-10-27','category':'tech','draft':False,'summary':'','label':'','body':'<h1>小节标题</h1><p>来自富文本编辑器的正文。</p><img src="/assets/uploads/check.png" alt="验证图片">'})
        image=self.root/'assets/uploads/check.png';image.parent.mkdir(exist_ok=True)
        image.write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jX1sAAAAASUVORK5CYII='))
        self.save();self.build()
        output=self.root/'_site';html=(output/'new-note.html').read_text()
        self.assertEqual(html.count('<h1>'),1)
        self.assertIn('包含 &lt; &amp; 的标题',html)
        self.assertIn('发布于 2026年10月27日',html)
        self.assertIn('<span>技术</span>',html)
        self.assertIn('"datePublished": "2026-10-27"',html)
        self.assertIn('content="article"',html)
        for name in ['articles.html','tech.html','sitemap.xml']:
            self.assertIn('new-note.html',(output/name).read_text())
        self.assertTrue((output/'assets/uploads/check.png').exists())
    def test_drafts_are_not_public_or_packaged(self):
        self.posts.append({'title':'未公开草稿','slug':'draft-only','category':'life','draft':True,'body':'<p>DRAFT_PRIVATE_FIXTURE</p>'})
        self.save();self.build();output=self.root/'_site'
        self.assertFalse((output/'draft-only.html').exists())
        for path in output.glob('*.html'):
            self.assertNotIn('DRAFT_PRIVATE_FIXTURE',path.read_text())
            self.assertNotIn('draft-only.html',path.read_text())
        for name in ['articles.json','.pages.yml','.git','scripts','README.md','.github']:
            self.assertFalse((output/name).exists(),name)
        self.assertNotIn('draft-only.html',(output/'sitemap.xml').read_text())
    def test_author_can_edit_existing_text_without_resetting_date(self):
        self.posts[0]['body']+='<p>作者自己更新的正文。</p>'
        self.save();self.build()
        html=(self.root/'_site/hello.html').read_text()
        self.assertIn('作者自己更新的正文。',html)
        self.assertIn('发布于 2026年10月24日',html)
    def test_invalid_content_leaves_previous_preview_untouched(self):
        self.build();old=(self.root/'_site/index.html').read_bytes()
        for key,value in [('datePublished',''),('datePublished','2026-02-30'),('slug','index.html'),('slug','../oops'),('body','')]:
            self.posts=json.loads(self.original);self.posts[0][key]=value;self.save();self.build(ok=False)
            self.assertEqual((self.root/'_site/index.html').read_bytes(),old)
    def test_unpublishing_removes_old_generated_page(self):
        self.build();self.posts[0]['draft']=True;self.save();self.build()
        output=self.root/'_site'
        self.assertFalse((output/'hello.html').exists())
        self.assertNotIn('hello.html',(output/'sitemap.xml').read_text())
        self.assertNotIn('给想法一个开始的地方',(output/'index.html').read_text())
    def test_empty_article_list_and_normalized_duplicates(self):
        self.posts=[];self.save();self.build()
        self.assertEqual(len(list((self.root/'_site').glob('*.html'))),7)
        self.posts=json.loads(self.original);copy=dict(self.posts[0]);copy['slug']='hello';self.posts.append(copy)
        self.save();self.build(ok=False)

if __name__=='__main__':unittest.main()
