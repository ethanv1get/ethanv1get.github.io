# -*- coding: utf-8 -*-
"""Validate CMS records without inventing dates or changing persisted content."""
from datetime import date
from html import unescape
from pathlib import Path
import json
import re

STATIC_PAGES = ('index.html', 'articles.html', 'tech.html', 'life.html', 'about.html', 'contact.html', '404.html')
CATEGORY_LABELS = {'life': '随笔', 'tech': '技术'}


def load_articles(path):
    records = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(records, list):
        raise ValueError('articles.json 必须是文章列表。')
    posts, seen = [], set()
    for index, record in enumerate(records, 1):
        if not isinstance(record, dict):
            raise ValueError(f'第 {index} 篇文章格式不正确。')
        post = dict(record)
        title = post.get('title', '')
        slug = post.get('slug', '')
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f'第 {index} 篇文章需要标题。')
        if not isinstance(slug, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*(?:\.html)?', slug.strip()):
            raise ValueError(f'《{title}》的网址需使用小写英文、数字和连字符。')
        slug = slug.strip()
        slug = slug if slug.endswith('.html') else slug + '.html'
        if slug in STATIC_PAGES:
            raise ValueError(f'《{title}》的网址 {slug} 与网站页面冲突，请换一个短名。')
        if slug in seen:
            raise ValueError(f'文章网址重复：{slug}。请使用不同的网址名称。')
        seen.add(slug)
        draft = post.get('draft', True)
        if not isinstance(draft, bool):
            raise ValueError(f'《{title}》的草稿开关必须为 true 或 false。')
        category = post.get('category', 'life')
        if category not in CATEGORY_LABELS:
            raise ValueError(f'《{title}》的分类必须是 life 或 tech。')
        published = post.get('datePublished') or ''
        if published:
            if not isinstance(published, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', published):
                raise ValueError(f'《{title}》的首次发布日期需使用 YYYY-MM-DD。')
            date.fromisoformat(published)
        elif not draft:
            raise ValueError(f'《{title}》正式发布前需要填写首次发布日期。')
        body = post.get('body') or ''
        if not isinstance(body, str):
            raise ValueError(f'《{title}》的正文格式不正确。')
        if not draft and not (re.sub(r'<[^>]+>', '', body).strip() or re.search(r'<(?:img|video|audio|iframe)\b', body, re.I)):
            raise ValueError(f'《{title}》正式发布前需要填写正文。')
        # The page itself owns h1; rich-text heading 1 becomes an article section.
        body = re.sub(r'<(/?)h1\b', r'<\1h2', body, flags=re.I)
        label = post.get('label') or CATEGORY_LABELS[category]
        summary = post.get('summary') or ''
        if not isinstance(label, str) or not isinstance(summary, str):
            raise ValueError(f'《{title}》的摘要或分类显示名称格式不正确。')
        if not summary.strip():
            summary = re.sub(r'\s+', ' ', unescape(re.sub(r'<[^>]+>', ' ', body))).strip()[:90]
        post.update(title=title.strip(), slug=slug, category=category, draft=draft,
                    datePublished=published, label=label, summary=summary.strip(), body=body)
        posts.append(post)
    return posts


def public_articles(posts):
    return sorted((p for p in posts if not p['draft']), key=lambda p: p['datePublished'], reverse=True)
