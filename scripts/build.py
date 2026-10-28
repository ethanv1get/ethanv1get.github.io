# -*- coding: utf-8 -*-
"""Build the existing static site using Python standard library only."""
from pathlib import Path
from html import escape, unescape
import json
import os
from content import load_articles, public_articles
import re
from datetime import date
ROOT=Path(__file__).resolve().parents[1]
ALL_POSTS=load_articles(ROOT/'articles.json')
POSTS=public_articles(ALL_POSTS)
OUTPUT=Path(os.environ.get('SITE_OUTPUT',str(ROOT))).resolve()
CURRENT='aria-current="page"'
BASE='https://ethanv1.top/'
def arrow(direction=None): return ''
def link(href,text,primary=False,direction='→'): return f'<a class="button {"primary" if primary else "secondary"}" href="{href}">{text}{"" if primary else " " + arrow(direction)}</a>'
def article_length(post):
    text = unescape(re.sub(r'<[^>]+>', ' ', post['body']))
    return len(re.findall(r'[\u3400-\u9fff]', text)) + len(re.findall(r'\b[A-Za-z0-9]+\b', text))


def publication_date(post):
    value = post.get('datePublished')
    if not value:
        if post.get('draft'):
            return ''
        raise ValueError(f"Published article {post['slug']} requires datePublished (YYYY-MM-DD).")
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValueError(f"Invalid publication date for {post['slug']}: use YYYY-MM-DD.")
    published = date.fromisoformat(value)
    return f'<time class="post-date" datetime="{published.isoformat()}">发布于 {published.year}年{published.month}月{published.day}日</time>'


# Validate every record before generating any page. Dates are editorial data, not build timestamps.
for post in POSTS:
    publication_date(post)


def structured_data(file, title, desc, canonical):
    person = {'@type': 'Person', '@id': BASE + '#ethan', 'name': 'ethan', 'url': BASE + 'about.html', 'sameAs': ['https://t.me/ETHANV1']}
    site = {'@type': 'WebSite', '@id': BASE + '#website', 'name': 'ethan.', 'url': BASE, 'inLanguage': 'zh-CN', 'publisher': {'@id': person['@id']}}
    page_type = {'about.html': 'AboutPage', 'contact.html': 'ContactPage', 'articles.html': 'CollectionPage', 'tech.html': 'CollectionPage', 'life.html': 'CollectionPage'}.get(file, 'WebPage')
    page = {'@type': page_type, '@id': canonical + '#page', 'url': canonical, 'name': title + ' · ethan.', 'description': desc, 'inLanguage': 'zh-CN', 'isPartOf': {'@id': site['@id']}, 'about': {'@id': person['@id']}}
    graph = [site, person, page]
    post = next((p for p in POSTS if p['slug'] == file), None)
    if post and not post['draft']:
        units = article_length(post)
        article = {'@type': 'BlogPosting', '@id': canonical + '#article', 'headline': post['title'], 'description': post['summary'], 'url': canonical, 'mainEntityOfPage': {'@id': page['@id']}, 'author': {'@id': person['@id']}, 'publisher': {'@id': person['@id']}, 'inLanguage': 'zh-CN', 'articleSection': post['label'], 'wordCount': units, 'image': BASE + 'assets/og.png'}
        # Publish a date only when it is actually present in the article data.
        if post.get('datePublished'):
            article['datePublished'] = post['datePublished']
        page['mainEntity'] = {'@id': article['@id']}
        graph.append(article)
    return {'@context': 'https://schema.org', '@graph': graph}


def card(p,i,level=3):
    return f'''<a class="post-card" href="{p['slug']}"><div class="post-info"><div class="meta"><span>{escape(p['label'])}</span>{publication_date(p)}{'<span class="badge">待确认草稿</span>' if p['draft'] else ''}</div><h{level}>{escape(p['title'])}</h{level}><p>{escape(p['summary'])}</p><span class="read-link">阅读文章</span></div></a>'''

def shell(file,title,desc,active,content):
    canonical=BASE+('' if file=='index.html' else file)
    nav=''.join(f'<a href="{url}" {CURRENT if key==active else ""}><span>{label}</span></a>' for key,url,label in [('home','index.html','首页'),('articles','articles.html','文章'),('about','about.html','关于'),('contact','contact.html','联系')])
    schema=structured_data(file, title, desc, canonical)
    return f'''<!doctype html>
<html lang="zh-CN"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#f7f8f5"><title>{escape(title)} · ethan.</title><meta name="description" content="{escape(desc)}">
{'<meta name="robots" content="noindex">' if file=='404.html' else ''}
<link rel="canonical" href="{canonical}"><meta property="og:type" content="{'article' if any(post['slug']==file for post in POSTS) else 'website'}"><meta property="og:locale" content="zh_CN"><meta property="og:site_name" content="ethan."><meta property="og:title" content="{escape(title)} · ethan."><meta property="og:description" content="{escape(desc)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{BASE}assets/og.png"><meta property="og:image:alt" content="ethan. 记录此刻，也探索未知。"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(title)} · ethan."><meta name="twitter:description" content="{escape(desc)}"><meta name="twitter:image" content="{BASE}assets/og.png">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="style.css?v=20261028-about-copy"><script src="site.js" defer></script><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False).replace('<', chr(92) + 'u003c')}</script></head>
<body id="top"><a class="skip" href="#main">跳到正文</a><div class="site-shell"><header class="site-header"><a class="brand" href="index.html" translate="no" aria-label="ethan. 首页">ethan<span>.</span></a><nav aria-label="主导航">{nav}</nav></header><main id="main" tabindex="-1">{content}</main>
<footer class="site-footer"><div class="footer-top"><div><a class="footer-brand" href="index.html" translate="no">ethan.</a><p>给好奇心留一点空间。</p></div><div class="footer-contact"><p class="footer-label">保持联系</p><div class="footer-links"><a href="https://t.me/ETHANV1">Telegram</a><a href="mailto:ethansunv1@gmail.com">写封邮件</a></div></div></div><div class="footer-bottom"><span>© <span data-year>2026</span> ethan</span><a class="to-top" href="#top">回到顶部 {arrow('↑')}</a></div></footer></div></body></html>'''

OUTPUT.mkdir(parents=True,exist_ok=True)
for post in ALL_POSTS:
    if post['draft'] and (OUTPUT/post['slug']).exists():
        (OUTPUT/post['slug']).unlink()
def write(file,title,desc,active,content): (OUTPUT/file).write_text(shell(file,title,desc,active,content),encoding='utf-8')
ring='''<div class="idea-mark" aria-hidden="true"><svg viewBox="0 0 420 420" fill="none"><circle cx="210" cy="210" r="180" fill="#e2ecf0"/><circle cx="210" cy="210" r="132" fill="#b8cbc6"/><circle cx="256" cy="236" r="68" fill="#315a79"/><circle cx="112" cy="112" r="28" fill="#dfb198"/></svg></div>'''
def empty_state(category='all'):
    if category == 'tech':
        return '<div class="empty"><span class="empty-symbol" aria-hidden="true">…</span><h2>技术文章，慢慢积累。</h2><p>这里将记录工具、实践与解决问题的过程。<br>第一篇技术文章尚未发布，先看看其他文字吧。</p><a class="text-link" href="articles.html">浏览全部文章 </a></div>'
    title, text = {
        'all': ('新的记录，正在路上。', '这里会陆续放下思考与生活中的发现。'),
        'tech': ('技术文章，慢慢积累。', '第一篇技术文章尚未发布，先看看其他文字吧。'),
        'life': ('生活记录，慢慢积累。', '这一栏还没有公开文章，先看看其他文字吧。'),
    }[category]
    return f'<div class="empty"><h2>{title}</h2><p>{text}</p><a class="text-link" href="articles.html">浏览全部文章</a></div>'

home=f'''<section class="hero" aria-labelledby="home-title"><div class="hero-composition"><div class="hero-copy"><h1 id="home-title"><span>记录此刻，</span><span>也探索未知。</span></h1><p>记录思考，探索技术，<br class="mobile-break">也收藏生活里值得记住的瞬间。</p><div class="actions">{link('articles.html','浏览文章',True)}{link('about.html','认识我')}</div></div></div></section>
<section class="selected section" id="selected" aria-labelledby="writing-title"><div class="section-head"><div><h2 id="writing-title">文章与记录</h2></div><a class="section-action" href="articles.html">全部文章</a></div>{''.join(card(p,i+1) for i,p in enumerate(POSTS[:3])) if POSTS else empty_state()}</section>
<section class="about-home section" aria-labelledby="about-title"><div><h2 id="about-title"><a class="about-title-link" href="about.html">关于 ethan</a></h2></div><div class="about-copy"><p>我把思考写下来，也把好奇变成尝试。<br>技术、日常和偶然的灵感，都在这里慢慢留下痕迹。</p></div></section>'''

write('index.html','记录此刻，也探索未知','ethan 的个人空间，记录思考、探索技术，也收藏生活里值得记住的瞬间。','home',home)

for filename,category,label in [('articles.html','all','全部'),('tech.html','tech','技术'),('life.html','life','生活')]:
    visible=[p for p in POSTS if category=='all' or p['category']==category]
    filters=''.join(f'<a class="filter" href="{f}" {CURRENT if c==category else ""}>{n}<span>{len([p for p in POSTS if c=="all" or p["category"]==c])}</span></a>' for f,c,n in [('articles.html','all','全部'),('tech.html','tech','技术'),('life.html','life','生活')])
    content=f'''<section class="page-heading"><h1>文章与记录</h1><p>技术与实践，生活与随笔。<br>不急着给出答案，先把值得思考的事情写下来。</p></section><section class="archive section" aria-label="{label}文章"><nav class="filters" aria-label="文章分类">{filters}</nav><div class="archive-results">{''.join(card(p,POSTS.index(p)+1,2) for p in visible) if visible else empty_state(category)}</div><p class="archive-note">{f'共 {len(visible)} 篇记录' if visible else '当前分类 0 篇记录'}{'，其中 1 篇为待确认草稿。' if any(p['draft'] for p in visible) else '。'}</p></section>'''
    write(filename,('文章' if category=='all' else label+'文章'),'ethan 的'+label+'文章与记录。'+('技术文章尚未发布，欢迎浏览其他文字。' if not visible else '关于思考、实践与生活的文字。'),'articles',content)

for p in POSTS:
    units = article_length(p)
    toc = ''
    body = p['body'].replace('<h2>保持好奇', '<h2 id="curiosity">保持好奇').replace('<h2>实现想法', '<h2 id="ideas">实现想法').replace('<h2>慢慢记录', '<h2 id="record">慢慢记录')
    if units >= 1200:
        headings = []
        def heading_anchor(match):
            attrs, inner = match.group(1), match.group(2)
            # Preserve existing links; only add an ID when the heading has none.
            old_id = re.search(r'id="([^"]+)"', attrs)
            anchor = old_id.group(1) if old_id else f'section-{len(headings)}'
            attrs = attrs if old_id else attrs + f' id="{anchor}"'
            headings.append((anchor, unescape(re.sub(r'<[^>]+>', '', inner))))
            return f'<h2{attrs}>{inner}</h2>'
        body = re.sub(r'<h2([^>]*)>(.*?)</h2>', heading_anchor, body, flags=re.S)
        toc_links = ''.join(f'<a href="#{escape(anchor)}">{escape(label)} {arrow("→")}</a>' for anchor, label in headings)
        if toc_links:
            toc = '<aside class="article-toc" aria-label="文章目录"><span>这篇文字里</span>' + toc_links + '</aside>'
    content=f'''<article class="article-page"><a class="text-link back-link" href="articles.html">{arrow('←')} 返回文章列表</a><header class="article-heading"><div class="meta"><span>{escape(p['label'])}</span>{publication_date(p)}{'<span class="badge">待确认草稿</span>' if p['draft'] else ''}</div><h1>{escape(p['title'])}</h1><p class="byline">文 / <span translate="no">ethan</span></p></header><div class="article-layout">{toc}<div class="prose">{'<p class="notice">这是一篇为展示博客阅读效果撰写的开站草稿，待 ethan 确认后再作为正式文章发布。</p>' if p['draft'] else ''}{body}<div class="article-end"><span class="end-dot" aria-hidden="true"></span><p>想法不必停在这里。</p><a class="text-link" href="contact.html">与 ethan 交流 {arrow('→')}</a></div><div class="article-bottom">{link('articles.html','返回文章列表')}</div></div></div></article>'''
    write(p['slug'],p['title'],p['summary']+(' 本文为待确认开站草稿。' if p['draft'] else ''),'articles',content)

write('about.html','关于','认识 ethan：最近在折腾 AI 工具，也在慢慢整理这个网站，记录技术上的尝试、生活里的观察，以及还没想明白的问题。','about',f'''<section class="page-heading about-heading"><h1>你好，我是 <span translate="no">ethan</span>。</h1></section><section class="about-detail section"><div class="about-body"><p>最近在折腾 AI 工具，也在慢慢整理这个网站。这里会放一些技术上的尝试、生活里的观察，还有暂时没想明白的问题。</p><p>我想把过程也记下来：为什么开始，试过什么，哪里卡住，最后有什么发现。</p><p>也欢迎你来聊聊自己的发现。</p><div class="actions">{link('contact.html','联系我',True)}{link('articles.html','浏览文章')}</div></div></section>''')

write('contact.html','联系','通过 Telegram @ETHANV1 联系 ethan，或写封邮件，聊聊你的问题、想法与日常发现。','contact',f'''<section class="page-heading"><h1>聊聊你的想法</h1><p>交流一个问题，分享一篇文章，<br>或者，简单打个招呼。</p></section><section class="contact-section section"><div class="contact-methods"><div class="contact-row"><a class="contact-method" href="https://t.me/ETHANV1"><span class="meta" translate="no">Telegram</span><span class="contact-value" translate="no">@ETHANV1</span><span class="contact-hint">打开 Telegram {arrow()}</span></a><button class="copy-button" type="button" data-copy="@ETHANV1" data-copy-label="Telegram 用户名" aria-label="复制 Telegram 用户名" hidden>复制用户名</button></div><div class="contact-row"><a class="contact-method" href="mailto:ethansunv1@gmail.com"><span class="meta">邮箱</span><span class="contact-value" translate="no">ethansunv1@gmail.com</span><span class="contact-hint">写封邮件 {arrow()}</span></a><button class="copy-button" type="button" data-copy="ethansunv1@gmail.com" data-copy-label="邮箱地址" aria-label="复制邮箱地址" hidden>复制邮箱</button></div><p class="copy-status" role="status" aria-live="polite" aria-atomic="true"></p><p class="muted contact-note">点击用户名打开 Telegram，<br>也可以扫描页面中的二维码添加好友。</p></div><figure class="qr-figure"><img loading="lazy" decoding="async" src="assets/telegram.jpg" width="1170" height="1363" alt="ethan 的 Telegram 加好友二维码，用户名 @ETHANV1"><figcaption>Telegram 二维码<br><span>@ETHANV1</span></figcaption></figure></section>''')
write('404.html','页面未找到','这个页面暂时没有内容。从首页或文章列表继续探索 ethan 的个人空间。','',f'''<section class="not-found"><span class="error-code" role="img" aria-label="错误 404">4<span class="error-zero" aria-hidden="true"></span>4</span><h1>想法还在，<br>这一页走丢了。</h1><p>这个地址可能已经移动，或暂时不存在。<br>换一个入口，继续探索。</p><div class="actions">{link('/index.html','返回首页',True)}{link('/articles.html','浏览文章')}</div></section>''')
# Root-relative assets/links for the custom 404 even when a missing URL is nested.
p=OUTPUT/'404.html'; html=p.read_text()
import re
html=re.sub(r'(href|src)="(?!https?:|mailto:|#|/)([^"]+)"',r'\1="/\2"',html); p.write_text(html)
(OUTPUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{BASE+("" if f=="index.html" else f)}</loc></url>' for f in dict.fromkeys(['index.html','articles.html','tech.html','life.html'] + [p['slug'] for p in POSTS] + ['about.html','contact.html']))+'</urlset>\n')
(OUTPUT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+BASE+'sitemap.xml\n')
print('Built',7+len(POSTS),'public pages;',len(POSTS),'published article(s).')

