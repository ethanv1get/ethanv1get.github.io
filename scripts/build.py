
# -*- coding: utf-8 -*-
"""Build the existing static site using Python standard library only."""
from pathlib import Path
from html import escape, unescape
import json
import os
from content import load_articles, public_articles, show_subscription_page, subscription_username, STATIC_PAGES, SUBSCRIBE_PAGE
import re
from datetime import date
ROOT=Path(__file__).resolve().parents[1]
ALL_POSTS=load_articles(ROOT/'articles.json')
POSTS=public_articles(ALL_POSTS)
OUTPUT=Path(os.environ.get('SITE_OUTPUT',str(ROOT))).resolve()
CURRENT='aria-current="page"'
BASE='https://ethanv1.top/'
buttondown_username = subscription_username(ROOT)
subscribe_enabled = show_subscription_page(ROOT)
subscribe_link = (
    f'<a class="button secondary pill subscribe-link" href="{SUBSCRIBE_PAGE}">邮件订阅更新</a>'
    if subscribe_enabled else ''
)
def arrow(direction=None): return ''
def link(href, text, primary=False, direction='→', *, pill=False):
    style = 'primary' if primary else 'secondary'
    shape = ' pill' if pill else ''
    suffix = '' if primary else ' ' + arrow(direction)
    return f'<a class="button {style}{shape}" href="{href}">{text}{suffix}</a>'
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
    page_type = {'about.html': 'AboutPage', 'contact.html': 'ContactPage', 'articles.html': 'CollectionPage', 'tech.html': 'CollectionPage', 'life.html': 'CollectionPage', 'works.html': 'CollectionPage'}.get(file, 'WebPage')
    page = {'@type': page_type, '@id': canonical + '#page', 'url': canonical, 'name': title + ' · ethan.', 'description': desc, 'inLanguage': 'zh-CN', 'isPartOf': {'@id': site['@id']}, 'about': {'@id': person['@id']}}
    graph = [site, person, page]
    post = next((p for p in POSTS if p['slug'] == file), None)
    if post and not post['draft']:
        units = article_length(post)
        article = {'@type': 'BlogPosting', '@id': canonical + '#article', 'headline': post['title'], 'description': post['summary'], 'url': canonical, 'mainEntityOfPage': {'@id': page['@id']}, 'author': {'@id': person['@id']}, 'publisher': {'@id': person['@id']}, 'inLanguage': 'zh-CN', 'articleSection': post['label'], 'wordCount': units, 'image': BASE + 'assets/og.png?v=20261030-cover'}
        # Publish a date only when it is actually present in the article data.
        if post.get('datePublished'):
            article['datePublished'] = post['datePublished']
        page['mainEntity'] = {'@id': article['@id']}
        graph.append(article)
    elif file == 'koin.html':
        app = {'@type': 'SoftwareApplication', '@id': canonical + '#app', 'name': 'Koin', 'operatingSystem': 'Android', 'applicationCategory': 'FinanceApplication', 'description': desc, 'url': canonical, 'author': {'@id': person['@id']}, 'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'CNY'}}
        page['mainEntity'] = {'@id': app['@id']}
        graph.append(app)
    return {'@context': 'https://schema.org', '@graph': graph}


def card(p,i,level=3):
    title_id = f'post-title-{i}'
    draft_badge = '<span class="badge">待确认草稿</span>' if p['draft'] else ''
    return f'''<a class="post-card" href="{p['slug']}" aria-labelledby="{title_id}">
      <div class="post-info">
        <div class="meta"><span>{escape(p['label'])}</span>{publication_date(p)}{draft_badge}</div>
        <h{level} id="{title_id}">{escape(p['title'])}</h{level}>
        <p>{escape(p['summary'])}</p>
      </div>
    </a>'''

def row(p):
    value = p.get('datePublished') or ''
    published = date.fromisoformat(value) if re.fullmatch(r'\d{4}-\d{2}-\d{2}', value) else None
    cn_date = f'<time datetime="{published.isoformat()}">{published.year}年{published.month}月{published.day}日</time>' if published else escape(value)
    return f'''<a class="home-tl-item" href="/{p['slug']}"><small>{escape(p['label'])} · {cn_date}</small><b>{escape(p['title'])}</b><p>{escape(p['summary'])}</p></a>'''

def shell(file,title,desc,active,content,extra_head=''):
    canonical=BASE+('' if file=='index.html' else file)
    nav=''.join(f'<a href="{url}" {CURRENT if key==active else ""}><span>{label}</span></a>' for key,url,label in [('home','index.html','首页'),('articles','articles.html','文章'),('works','works.html','作品'),('about','about.html','关于'),('contact','contact.html','联系')])
    schema=structured_data(file, title, desc, canonical)
    return f'''<!doctype html>
<html lang="zh-CN"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#fafaf9" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#1b1b1d" media="(prefers-color-scheme: dark)"><title>{escape(title)} · ethan.</title><meta name="description" content="{escape(desc)}">
{'<meta name="robots" content="noindex">' if file == '404.html' or (file == SUBSCRIBE_PAGE and not buttondown_username) else ''}
<link rel="canonical" href="{canonical}"><meta property="og:type" content="{'article' if any(post['slug']==file for post in POSTS) else 'website'}"><meta property="og:locale" content="zh_CN"><meta property="og:site_name" content="ethan."><meta property="og:title" content="{escape(title)} · ethan."><meta property="og:description" content="{escape(desc)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{BASE}assets/og.png?v=20261030-cover"><meta property="og:image:alt" content="ethan. 记录此刻，也探索未知。"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(title)} · ethan."><meta name="twitter:description" content="{escape(desc)}"><meta name="twitter:image" content="{BASE}assets/og.png?v=20261030-cover">
<link rel="icon" href="assets/favicon.svg?v=20261121-cover" type="image/svg+xml"><link rel="stylesheet" href="assets/theme.css?v=20261121-cover"><link rel="stylesheet" href="style.css?v=20261122-works"><script src="site.js?v=20261030-print-edition" defer></script>{extra_head}<script type="application/ld+json">{json.dumps(schema,ensure_ascii=False).replace('<', chr(92) + 'u003c')}</script></head>
<body id="top"><a class="skip" href="#main">跳到正文</a><div class="site-shell"><header class="site-header"><a class="brand" href="index.html" translate="no" aria-label="ethan. 首页"><img class="brand-avatar" src="assets/avatar.jpg" alt="" width="28" height="28" decoding="async"><span>ethan<i>.</i></span></a><nav aria-label="主导航">{nav}</nav></header><main id="main" tabindex="-1">{content}</main>
<footer class="site-footer"><div class="footer-top"><div><a class="footer-brand" href="index.html" translate="no">ethan.</a><p>给好奇心留一点空间。</p></div><div class="footer-contact"><p class="footer-label">保持联系</p><div class="footer-links"><a href="https://t.me/ETHANV1">Telegram</a><a href="mailto:ethansunv1@gmail.com">写封邮件</a></div></div></div><div class="footer-bottom"><span>© <span data-year>2026</span> ethan</span><a class="to-top" href="#top">回到顶部 {arrow('↑')}</a></div></footer></div></body></html>'''

OUTPUT.mkdir(parents=True,exist_ok=True)
for post in ALL_POSTS:
    if post['draft'] and (OUTPUT/post['slug']).exists():
        (OUTPUT/post['slug']).unlink()
def write(file,title,desc,active,content,extra_head=''): (OUTPUT/file).write_text(shell(file,title,desc,active,content,extra_head),encoding='utf-8')
page_video=''
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

home='''<section class="hero" aria-labelledby="home-title"><div class="hero-copy"><h1 id="home-title">记录此刻，也探索未知。</h1></div></section>'''

write('index.html','记录此刻，也探索未知','ethan 的个人空间，记录思考、探索技术，也收藏生活里值得记住的瞬间。','home',home)

archive_subscribe = f'<div class="archive-subscribe">{subscribe_link}</div>' if subscribe_link else ''
for filename,category,label in [('articles.html','all','全部'),('tech.html','tech','技术'),('life.html','life','生活')]:
    visible=[p for p in POSTS if category=='all' or p['category']==category]
    counts={c:len([p for p in POSTS if c=='all' or p['category']==c]) for c in ('all','tech','life')}
    filters=''.join(f'<a class="filter" href="{f}" {CURRENT if c==category else ""}>{n}<span>{counts[c]}</span></a>' for f,c,n in [('articles.html','all','全部'),('tech.html','tech','技术'),('life.html','life','生活')] if c=='all' or c==category or counts[c])
    content = f'''<section class="page-heading">{page_video}<h1>文章与记录</h1><p>技术与实践，生活与随笔。<br>不急着给出答案，先把值得思考的事情写下来。</p></section>
    <section class="archive section" aria-label="{label}文章">
      <div class="archive-toolbar">
        <nav class="filters" aria-label="文章分类">{filters}</nav>
        {archive_subscribe}
      </div>
      <div class="archive-results">{''.join(card(p,i,2) for i,p in enumerate(visible,1)) if visible else empty_state(category)}</div>
      <p class="archive-note">{f'共 {len(visible)} 篇记录' if visible else '当前分类 0 篇记录'}{'，其中 1 篇为待确认草稿。' if any(p['draft'] for p in visible) else '。'}</p>
    </section>'''
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
    article_actions = f'''<div class="article-end"><span class="end-dot" aria-hidden="true"></span><p>想法不必停在这里。</p>
      <div class="article-actions">
        <a class="text-link" href="contact.html">与 ethan 交流</a>
        {subscribe_link}
        <div class="article-bottom">{link('articles.html','返回文章列表',pill=True)}</div>
      </div>
    </div>'''
    content=f'''<article class="article-page"><div class="article-masthead">{page_video}<a class="text-link back-link" href="articles.html">{arrow('←')} 返回文章列表</a><header class="article-heading"><div class="meta"><span>{escape(p['label'])}</span>{publication_date(p)}{'<span class="badge">待确认草稿</span>' if p['draft'] else ''}</div><h1>{escape(p['title'])}</h1><p class="byline">文 / <span translate="no">ethan</span></p></header></div><div class="article-layout">{toc}<div class="prose">{'<p class="notice">这是一篇为展示博客阅读效果撰写的开站草稿，待 ethan 确认后再作为正式文章发布。</p>' if p['draft'] else ''}{body}{article_actions}</div></div></article>'''
    write(p['slug'],p['title'],p['summary']+(' 本文为待确认开站草稿。' if p['draft'] else ''),'articles',content)

write('about.html','关于','认识 ethan：最近在折腾 AI 工具，也在慢慢整理这个网站，记录技术上的尝试、生活里的观察，以及还没想明白的问题。','about',f'''<section class="page-heading about-heading">{page_video}<h1>你好，我是 <span translate="no">ethan</span>。</h1></section><section class="about-detail section"><aside class="about-margin"><span>关注的方向</span><p>AI 工具<br>技术实践<br>生活观察</p></aside><div class="about-body"><p>最近在折腾 AI 工具，也在慢慢整理这个网站。这里会放一些技术上的尝试、生活里的观察，还有暂时没想明白的问题。</p><p>我想把过程也记下来：为什么开始，试过什么，哪里卡住，最后有什么发现。</p><p>也欢迎你来聊聊自己的发现。</p><div class="actions">{link('articles.html','浏览文章',pill=True)}{link('works.html','看看作品',pill=True)}{link('contact.html','联系我',True,pill=True)}</div></div></section>''')

write('contact.html','联系','通过 Telegram @ETHANV1 联系 ethan，或写封邮件，聊聊你的问题、想法与日常发现。','contact',f'''<section class="page-heading">{page_video}<h1>聊聊你的想法</h1><p>交流一个问题，分享一篇文章，<br>或者，简单打个招呼。</p></section><section class="contact-section section"><div class="contact-icons"><a class="contact-icon" href="https://t.me/ETHANV1" aria-label="在 Telegram 上联系 ethan"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></svg><span>Telegram</span></a><a class="contact-icon" href="mailto:ethansunv1@gmail.com" aria-label="给 ethan 写邮件"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/></svg><span>Email</span></a></div></section>''')
if subscribe_enabled:
    if buttondown_username:
        form = f'''<form class="subscribe-form" action="https://buttondown.com/api/emails/embed-subscribe/{escape(buttondown_username)}" method="post">
          <label for="subscribe-email">你的邮箱</label>
          <div class="subscribe-fields">
            <input id="subscribe-email" name="email" type="email" autocomplete="email" inputmode="email" placeholder="you@example.com" aria-describedby="subscribe-help" required>
            <input type="hidden" name="embed" value="1">
            <button class="button primary pill" type="submit">订阅更新</button>
          </div>
          <p class="subscribe-help" id="subscribe-help">提交后，请在邮件里确认订阅。每封更新邮件都可以退订。</p>
        </form>'''
    else:
        form = '''<div class="subscribe-form" aria-label="邮件订阅布局预览">
          <label for="subscribe-email">你的邮箱</label>
          <div class="subscribe-fields">
            <input id="subscribe-email" type="email" placeholder="you@example.com" disabled>
            <button class="button primary pill" type="button" disabled>订阅更新</button>
          </div>
          <p class="subscribe-help" role="status">本地预览，正在绑定订阅账号。</p>
        </div>'''
    write(
        SUBSCRIBE_PAGE, '邮件订阅', '通过邮件收到 ethan. 的新文章，随时可以退订。', 'articles',
        f"""
        <section class="page-heading subscribe-heading">
          <h1>把新文章寄给你。</h1>
          <p>有新文章时，把标题、摘要和原文链接发到你的邮箱。</p>
        </section>
        <section class="subscribe-details" aria-label="订阅新文章">
          {form}
          <p class="subscribe-provider">订阅和邮件发送由 <a href="https://buttondown.com/" rel="external">Buttondown</a> 提供。</p>
        </section>
        <a class="text-link subscribe-back" href="articles.html">返回文章</a>
        """,
    )
else:
    (OUTPUT / SUBSCRIBE_PAGE).unlink(missing_ok=True)

koin_version = '1.0.10'
koin_updated = '2026-11-22'
koin_notes = '启动页底部新增极简版权声明小字（© 2026 Koin · Ethan · All Rights Reserved），深浅色模式自动适配，随启动封面柔和淡入淡出。'
koin_sha256 = 'd3284229c03766c507280f6fbbf010409fb48e1e951db8d88bbd6eefb2b75b31'
koin_origin = f'https://github.com/ethanv1get/koin/releases/download/v{koin_version}/Koin-v{koin_version}-arm64.apk'
koin_primary = f'https://tvv.tw/{koin_origin}'
koin_emblem = '''<svg class="koin-emblem" viewBox="0 0 64 64" width="60" height="60" fill="none" aria-hidden="true">
  <defs>
    <linearGradient id="koin-seg-0" gradientUnits="userSpaceOnUse" x1="32.0" y1="4.72" x2="59.28" y2="32.48"><stop offset="0%" stop-color="#EC4899"/><stop offset="100%" stop-color="#8B5CF6"/></linearGradient>
    <linearGradient id="koin-seg-1" gradientUnits="userSpaceOnUse" x1="59.28" y1="32.0" x2="31.52" y2="59.28"><stop offset="0%" stop-color="#8B5CF6"/><stop offset="100%" stop-color="#F97316"/></linearGradient>
    <linearGradient id="koin-seg-2" gradientUnits="userSpaceOnUse" x1="32.0" y1="59.28" x2="4.72" y2="31.52"><stop offset="0%" stop-color="#F97316"/><stop offset="100%" stop-color="#3B82F6"/></linearGradient>
    <linearGradient id="koin-seg-3" gradientUnits="userSpaceOnUse" x1="4.72" y1="32.0" x2="32.48" y2="4.72"><stop offset="0%" stop-color="#3B82F6"/><stop offset="100%" stop-color="#EC4899"/></linearGradient>
  </defs>
  <path d="M 59.28 32.48 A 27.28 27.28 0 0 0 32.0 4.72" stroke="url(#koin-seg-0)" stroke-width="5.44" stroke-linecap="round"/>
  <path d="M 31.52 59.28 A 27.28 27.28 0 0 0 59.28 32.0" stroke="url(#koin-seg-1)" stroke-width="5.44" stroke-linecap="round"/>
  <path d="M 4.72 31.52 A 27.28 27.28 0 0 0 32.0 59.28" stroke="url(#koin-seg-2)" stroke-width="5.44" stroke-linecap="round"/>
  <path d="M 32.48 4.72 A 27.28 27.28 0 0 0 4.72 32.0" stroke="url(#koin-seg-3)" stroke-width="5.44" stroke-linecap="round"/>
  <path d="M 25.6 21.12 L 25.6 42.88 M 39.04 21.76 L 26.88 32 L 39.68 42.88" stroke="currentColor" stroke-width="4.35" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="40.32" cy="21.76" r="1.8" fill="#EC4899"/>
</svg>'''

works_content = f'''<section class="page-heading">{page_video}<h1>作品与工具</h1><p>自己动手做出来的小应用与工具，欢迎下载体验，也欢迎随时聊聊反馈。</p></section>
<section class="works-section section" aria-label="作品列表">
  <article class="work-card" aria-labelledby="work-koin-title">
    <div class="work-card-main">
      <div class="work-card-head">
        <div class="work-icon-box">{koin_emblem}</div>
        <div class="work-head-copy">
          <div class="work-title-row">
            <h2 id="work-koin-title" translate="no">Koin</h2>
            <span class="koin-ver" data-koin-version>v{koin_version}</span>
            <span class="work-status">可下载体验</span>
          </div>
          <p class="work-tagline">轻盈记账 · 每一笔清晰可见</p>
        </div>
      </div>
      <p class="work-desc">自己做的极简 Android 本地记账应用。账单、预算与银行渠道全部留在手机本地，不上传云端；支持双击音量下键、下拉快捷磁贴或桌面入口直接拉起悬浮窗随时闪记，并在应用内直接覆盖更新。</p>
      <div class="work-tags" aria-label="特点">
        <span>Android · arm64-v8a</span>
        <span>本地离线 · 免费</span>
        <span>四色预算环</span>
        <span>悬浮窗闪记</span>
        <time class="work-updated" datetime="{koin_updated}" data-koin-updated>更新于 {koin_updated}</time>
      </div>
    </div>
    <div class="work-actions">
      <a class="button primary pill" href="koin.html">体验与下载 Koin</a>
      <a class="text-link" href="contact.html">提个建议或反馈</a>
    </div>
  </article>
  <p class="archive-note">目前收录 1 件作品，后续做出新东西也会陆续放在这里。</p>
</section>'''

write(
    'works.html',
    '作品',
    'ethan 自己动手做的小应用与工具。目前收录 Android 极简本地记账应用 Koin，欢迎下载体验。',
    'works',
    works_content,
    extra_head='<script src="assets/koin.js?v=20261122-sync2" defer></script>',
)

koin_content = f'''<section class="koin-page" aria-labelledby="koin-title">
  <a class="text-link back-link koin-back" href="works.html">{arrow('←')} 返回作品列表</a>
  <aside id="koin-wechat-tip" class="koin-wechat-tip" hidden>
    <p class="koin-wechat-title">在微信内打开，请切到系统浏览器下载</p>
    <p class="koin-wechat-desc">微信内置浏览器不支持直接下载安装包。请点击右上角「···」，选择「在浏览器打开」即可一键下载；也可以复制本页链接到手机自带浏览器打开。</p>
    <div class="koin-wechat-actions">
      <button id="koin-copy-page" class="button secondary pill" type="button">复制本页链接</button>
    </div>
  </aside>

  <div class="koin-hero">
    <div class="koin-icon-box">{koin_emblem}</div>
    <div class="koin-intro">
      <div class="koin-title-row">
        <h1 id="koin-title" translate="no">Koin</h1>
        <span class="koin-ver" data-koin-version>v{koin_version}</span>
      </div>
      <p class="koin-tagline">轻盈记账 · 每一笔清晰可见</p>
      <div class="koin-meta-tags">
        <span>Android · arm64-v8a</span>
        <span>约 33 MB</span>
        <span>本地离线 · 免费</span>
      </div>
    </div>
  </div>

  <div class="koin-download-card">
    <div class="koin-actions">
      <a id="koin-download-btn" class="button primary pill koin-primary-btn" href="{koin_primary}">下载 Android 安装包（v{koin_version}）</a>
      <button id="koin-copy-url" class="button secondary pill" type="button" data-copy-url="{koin_primary}">复制下载直链</button>
    </div>
    <p id="koin-status" class="koin-status" role="status" aria-live="polite"></p>
    <div class="koin-notes-box">
      <span class="koin-label">更新说明</span>
      <p data-koin-notes>{escape(koin_notes)}</p>
    </div>
    <div class="koin-mirrors" id="koin-mirrors">
      <span class="koin-label">备用下载线路</span>
      <div class="koin-mirror-links">
        <a data-koin-mirror="tvv" href="https://tvv.tw/{koin_origin}" rel="external">国内线路 1</a>
        <a data-koin-mirror="ghproxy" href="https://gh-proxy.org/{koin_origin}" rel="external">国内线路 2</a>
        <a data-koin-mirror="edgeone" href="https://edgeone.gh-proxy.org/{koin_origin}" rel="external">国内线路 3</a>
        <a data-koin-mirror="origin" href="{koin_origin}" rel="external">GitHub 原链</a>
        <a data-koin-mirror="release" href="https://github.com/ethanv1get/koin/releases/tag/v{koin_version}" rel="external">发布页</a>
      </div>
    </div>
  </div>

  <div class="koin-features">
    <div class="koin-feature">
      <h2>本地保存</h2>
      <p>账单、预算与银行渠道全部存在手机本地，不上传云端，联网仅用于检查软件更新。</p>
    </div>
    <div class="koin-feature">
      <h2>随时闪记</h2>
      <p>支持双击音量下键、下拉快捷磁贴或桌面快捷入口直接拉起悬浮窗记一笔。</p>
    </div>
    <div class="koin-feature">
      <h2>平滑升级</h2>
      <p>安装后在右上角快捷入口即可检查更新，新版本覆盖安装自动保留全部本地账单。</p>
    </div>
  </div>

  <div class="koin-install-notes">
    <h2>安装说明</h2>
    <ul>
      <li>目前仅提供 Android 64 位安装包（<code>arm64-v8a</code>）。</li>
      <li>如在微信内打不开下载，请点右上角「···」选择「在浏览器打开」，再点击下载按钮。</li>
      <li>安装时若系统提示「允许安装未知来源应用」，授权后继续即可；旧版用户直接覆盖安装，原有账单不会丢失。</li>
    </ul>
    <p class="koin-checksum">SHA-256：<code data-koin-sha256>{koin_sha256}</code></p>
  </div>
</section>'''

write(
    'koin.html',
    'Koin · Android 下载',
    '轻盈极简的个人本地记账应用 Koin（Android），支持全局悬浮闪记、预算圆环统计与应用内覆盖更新。',
    'works',
    koin_content,
    extra_head='<script src="assets/koin.js?v=20261122-sync2" defer></script>',
)

write('404.html','页面未找到','这个页面暂时没有内容。从首页或文章列表继续探索 ethan 的个人空间。','',f'''<section class="not-found">{page_video}<span class="error-code" role="img" aria-label="错误 404">4<span class="error-zero" aria-hidden="true"></span>4</span><h1>想法还在，<br>这一页走丢了。</h1><p>这个地址可能已经移动，或暂时不存在。<br>换一个入口，继续探索。</p><div class="actions">{link('/index.html','返回首页',True)}{link('/articles.html','浏览文章')}</div></section>''')
# Root-relative assets/links for the custom 404 even when a missing URL is nested.
p=OUTPUT/'404.html'; html=p.read_text()
import re
html=re.sub(r'(href|src)="(?!https?:|mailto:|#|/)([^"]+)"',r'\1="/\2"',html); p.write_text(html)
(OUTPUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{BASE+("" if f=="index.html" else f)}</loc></url>' for f in dict.fromkeys(['index.html','articles.html','tech.html','life.html','works.html'] + [p['slug'] for p in POSTS] + ['about.html','contact.html','koin.html'] + ([SUBSCRIBE_PAGE] if buttondown_username else [])))+'</urlset>\n')
(OUTPUT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+BASE+'sitemap.xml\n')
print('Built',len(STATIC_PAGES)+len(POSTS)+int(subscribe_enabled),'public pages;',len(POSTS),'published article(s).')

