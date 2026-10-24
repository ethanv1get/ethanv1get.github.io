"""Build the existing static site using Python standard library only."""
from pathlib import Path
from html import escape
import json
ROOT=Path(__file__).resolve().parents[1]
POSTS=json.loads((ROOT/'articles.json').read_text())
CURRENT='aria-current="page"'
BASE='https://ethanv1.top/'
def arrow(direction='↗'): return f'<span class="arrow" aria-hidden="true">{direction}</span>'
def link(href,text,primary=False,direction='↗'): return f'<a class="button {"primary" if primary else "secondary"}" href="{href}">{text} {arrow(direction)}</a>'
def card(p,i,level=3):
    return f'''<a class="post-card" href="{p['slug']}"><div class="post-cover" aria-hidden="true"><span class="cover-dot"></span></div><div class="post-info"><div class="meta"><span>{p['label']}</span>{'<span class="badge">待确认草稿</span>' if p['draft'] else ''}</div><h{level}>{escape(p['title'])}</h{level}><p>{escape(p['summary'])}</p><span class="read-link">阅读全文 {arrow()}</span></div></a>'''
def shell(file,title,desc,active,content):
    canonical=BASE+('' if file=='index.html' else file)
    nav=''.join(f'<a href="{url}" {CURRENT if key==active else ""}><span>{label}</span></a>' for key,url,label in [('home','index.html','首页'),('articles','articles.html','文章'),('about','about.html','关于'),('contact','contact.html','联系')])
    schema={'@context':'https://schema.org','@type':'WebSite','name':'ethan.','url':BASE,'description':'一个关于好奇心、思考与创造的个人空间。'}
    return f'''<!doctype html>
<html lang="zh-CN"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#f6f5f0"><title>{escape(title)} · ethan.</title><meta name="description" content="{escape(desc)}">
{'<meta name="robots" content="noindex">' if file=='404.html' else ''}
<link rel="canonical" href="{canonical}"><meta property="og:type" content="{'article' if file=='hello.html' else 'website'}"><meta property="og:locale" content="zh_CN"><meta property="og:site_name" content="ethan."><meta property="og:title" content="{escape(title)} · ethan."><meta property="og:description" content="{escape(desc)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{BASE}assets/og.png"><meta property="og:image:alt" content="ethan. 记录此刻，也探索未知。"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(title)} · ethan."><meta name="twitter:description" content="{escape(desc)}"><meta name="twitter:image" content="{BASE}assets/og.png">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="style.css"><script src="site.js" defer></script><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False)}</script></head>
<body id="top"><a class="skip" href="#main">跳到正文</a><div class="site-shell"><header class="site-header"><a class="brand" href="index.html" translate="no" aria-label="ethan. 首页">ethan<span>.</span></a><nav aria-label="主导航">{nav}</nav></header><main id="main" tabindex="-1">{content}</main>
<footer class="site-footer"><div class="footer-top"><div><a class="footer-brand" href="index.html" translate="no">ethan.</a><p>给好奇心留一点空间。</p></div><div class="footer-links"><a href="https://t.me/ETHANV1">Telegram {arrow()}</a><a href="mailto:ethansunv1@gmail.com">写封邮件 {arrow()}</a></div></div><div class="footer-bottom"><span>© <span data-year>2026</span> ethan</span><a class="to-top" href="#top">回到顶部 {arrow('↑')}</a></div></footer></div></body></html>'''

def write(file,title,desc,active,content): (ROOT/file).write_text(shell(file,title,desc,active,content))
ring='''<div class="idea-mark" aria-hidden="true"><svg viewBox="0 0 420 420" fill="none"><circle cx="210" cy="210" r="180" fill="#e2ecf0"/><circle cx="210" cy="210" r="132" fill="#b8cbc6"/><circle cx="256" cy="236" r="68" fill="#315a79"/><circle cx="112" cy="112" r="28" fill="#dfb198"/></svg></div>'''
home=f'''<section class="hero"><div class="hero-composition"><div class="hero-copy"><h1><span>记录此刻，</span><span>也探索未知。</span></h1><p>记录思考，探索技术，<br class="mobile-break">也收藏生活里值得记住的瞬间。</p><div class="actions">{link('articles.html','探索文章',True)}{link('about.html','关于我',direction='→')}</div></div>{ring}</div></section>
<section class="selected section" id="selected"><div class="section-head"><div><h2>精选文章</h2></div><a class="text-link" href="articles.html">查看全部文章 {arrow('→')}</a></div>{''.join(card(p,i+1) for i,p in enumerate(POSTS[:3]))}</section>
<section class="about-home section"><div><h2>关于我<span class="accent">。</span></h2></div><div class="about-copy"><p>我把思考写下来，也把好奇变成尝试。<br>技术、日常和偶然的灵感，都在这里慢慢留下痕迹。</p><a class="text-link" href="about.html">进一步了解 {arrow('→')}</a></div></section>'''
write('index.html','记录此刻，也探索未知','ethan 的个人空间，记录思考、探索技术，也收藏生活里值得记住的瞬间。','home',home)

for filename,category,label in [('articles.html','all','全部'),('tech.html','tech','技术'),('life.html','life','生活')]:
    visible=[p for p in POSTS if category=='all' or p['category']==category]
    filters=''.join(f'<a class="filter" href="{f}" {CURRENT if c==category else ""}>{n}<span>{len([p for p in POSTS if c=="all" or p["category"]==c])}</span></a>' for f,c,n in [('articles.html','all','全部'),('tech.html','tech','技术'),('life.html','life','生活')])
    content=f'''<section class="page-heading"><span class="section-kicker">文字让想法有迹可循</span><h1>文章与记录<span class="accent">.</span></h1><p>技术与实践，生活与随笔。<br>不急着给出答案，先把值得思考的事情写下来。</p></section><section class="archive section" aria-label="{label}文章"><nav class="filters" aria-label="文章分类">{filters}</nav><div class="archive-results">{''.join(card(p,POSTS.index(p)+1,2) for p in visible) if visible else '<div class="empty"><span class="empty-symbol" aria-hidden="true">…</span><h2>技术文章，慢慢积累。</h2><p>这里将记录工具、实践与解决问题的过程。<br>第一篇技术文章尚未发布，先看看其他文字吧。</p><a class="text-link" href="articles.html">浏览全部文章 '+arrow('→')+'</a></div>'}</div><p class="archive-note">{f'共 {len(visible)} 篇记录' if visible else '当前分类 0 篇记录'}{'，其中 1 篇为待确认草稿。' if any(p['draft'] for p in visible) else '。'}</p></section>'''
    write(filename,('文章' if category=='all' else label+'文章'),'ethan 的'+label+'文章与记录。'+('技术文章尚未发布，欢迎浏览其他文字。' if not visible else '关于思考、实践与生活的文字。'),'articles',content)

for p in POSTS:
    content=f'''<article class="article-page"><a class="text-link back-link" href="articles.html">{arrow('←')} 返回文章列表</a><header class="article-heading"><div class="meta"><span>{p['label']}</span>{'<span class="badge">待确认草稿</span>' if p['draft'] else ''}</div><h1>{p['title']}</h1><p class="byline">文 / ethan</p></header><div class="article-layout"><aside class="article-toc" aria-label="文章目录"><span>这篇文字里</span><a href="#curiosity">保持好奇 {arrow('↘')}</a><a href="#ideas">实现想法 {arrow('↘')}</a><a href="#record">慢慢记录 {arrow('↘')}</a></aside><div class="prose">{'<p class="notice">这是一篇为展示博客阅读效果撰写的开站草稿，待 ethan 确认后再作为正式文章发布。</p>' if p['draft'] else ''}{p['body'].replace('<h2>保持好奇','<h2 id="curiosity">保持好奇').replace('<h2>实现想法','<h2 id="ideas">实现想法').replace('<h2>慢慢记录','<h2 id="record">慢慢记录')}<div class="article-end"><span class="end-dot" aria-hidden="true"></span><p>想法不必停在这里。</p><a class="text-link" href="contact.html">与 ethan 交流 {arrow('↗')}</a></div><div class="article-bottom">{link('articles.html','返回文章列表')}</div></div></div></article>'''
    write(p['slug'],p['title'],p['summary']+(' 本文为待确认开站草稿。' if p['draft'] else ''),'articles',content)

write('about.html','关于','认识 ethan：用好奇心探索技术与生活，把思考、实践和日常灵感记录在自己的个人空间。','about',f'''<section class="page-heading about-heading"><span class="section-kicker">A little about me.</span><h1>让好奇心，<br>一直有回声。</h1><p>你好，我是 ethan。欢迎来到我的个人空间。</p></section><section class="about-detail section"><div class="about-label"><svg class="about-mark" viewBox="0 0 240 240" aria-hidden="true"><circle cx="120" cy="120" r="105" fill="none" stroke="currentColor"/><circle cx="120" cy="120" r="76" fill="none" stroke="currentColor"/><circle cx="146" cy="136" r="38" fill="currentColor"/></svg><p>思考。探索。记录。</p></div><div class="about-body"><p class="large-copy">这里既有认真思考的片段，<br>也有生活中值得留下的细节。</p><p>我对新技术保持好奇，也喜欢把想法写下来。在学习与探索中，记录问题、动手的过程，以及那些还没有答案的思考。</p><h2>这个博客</h2><p>技术与实践，记录从问题到解法的过程；生活与随笔，留住观察、感受和偶然的灵感。让专业与日常，在同一个地方自然相遇。</p><h2>从交流开始</h2><p>如果某篇文字让你产生共鸣，或你有想交流的想法，欢迎联系我。</p><div class="actions">{link('contact.html','查看联系方式',True)}{link('articles.html','读一些文字')}</div></div></section>''')
write('contact.html','联系','通过 Telegram @ETHANV1 联系 ethan，或写封邮件，聊聊你的问题、想法与日常发现。','contact',f'''<section class="page-heading"><span class="section-kicker">交流从一句你好开始</span><h1>聊聊你的想法<span class="accent">.</span></h1><p>交流一个问题，分享一篇文章，<br>或者，简单打个招呼。</p></section><section class="contact-section section"><div class="contact-methods"><a class="contact-method" href="https://t.me/ETHANV1"><span class="meta">Telegram</span><span class="contact-value">@ETHANV1</span><span class="contact-hint">打开 Telegram {arrow()}</span></a><a class="contact-method" href="mailto:ethansunv1@gmail.com"><span class="meta">邮箱</span><span class="contact-value">ethansunv1@gmail.com</span><span class="contact-hint">写封邮件 {arrow()}</span></a><p class="muted contact-note">点击用户名打开 Telegram，<br>也可以扫描页面中的二维码添加好友。</p></div><figure class="qr-figure"><img src="assets/telegram.jpg" width="1170" height="1363" alt="ethan 的 Telegram 加好友二维码，用户名 @ETHANV1"><figcaption>扫一扫，保持联系。<br><span>@ETHANV1</span></figcaption></figure></section>''')
write('404.html','页面未找到','这个页面暂时没有内容。从首页或文章列表继续探索 ethan 的个人空间。','',f'''<section class="not-found"><span class="error-code" role="img" aria-label="错误 404">4<span class="error-zero" aria-hidden="true"></span>4</span><h1>想法还在，<br>这一页走丢了。</h1><p>这个地址可能已经移动，或暂时不存在。<br>换一个入口，继续探索。</p><div class="actions">{link('/index.html','返回首页',True)}{link('/articles.html','浏览文章')}</div></section>''')
# Root-relative assets/links for the custom 404 even when a missing URL is nested.
p=ROOT/'404.html'; html=p.read_text()
import re
html=re.sub(r'(href|src)="(?!https?:|mailto:|#|/)([^"]+)"',r'\1="/\2"',html); p.write_text(html)
(ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{BASE+("" if f=="index.html" else f)}</loc></url>' for f in ['index.html','articles.html','tech.html','life.html','hello.html','about.html','contact.html'])+'</urlset>\n')
(ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+BASE+'sitemap.xml\n')
print('Built 8 pages; retained',len(POSTS),'original article(s).')

