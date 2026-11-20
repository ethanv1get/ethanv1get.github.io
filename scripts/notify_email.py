"""Send new article notices through Buttondown after a successful deployment."""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import uuid
from html import escape
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from content import load_articles, public_articles, subscription_username, validate_articles

ROOT = Path(__file__).resolve().parents[1]
SITE = 'https://ethanv1.top/'
BUTTONDOWN = 'https://api.buttondown.com/v1'
TAG_PREFIX = 'email-notified/'


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, url):
        return None


def request(url, *, method='GET', headers=None, body=None):
    headers = {'User-Agent': 'ethan-site-email-notify', **(headers or {})}
    if body is not None:
        headers['Content-Type'] = 'application/json'
        body = json.dumps(body, ensure_ascii=False).encode('utf-8')
    req = Request(url, method=method, headers=headers, data=body)
    with build_opener(NoRedirect()).open(req, timeout=15) as response:
        return response.read()


class ArticleReservations:
    def __init__(self, repository, token, revision):
        self.url = f'https://api.github.com/repos/{repository}/git'
        self.headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github+json'}
        self.revision = revision

    def exists(self, slug):
        try:
            data = request(f'{self.url}/ref/tags/{TAG_PREFIX}{slug}', headers=self.headers)
            return json.loads(data)['ref'] == f'refs/tags/{TAG_PREFIX}{slug}'
        except HTTPError as error:
            if error.code == 404:
                return False
            raise

    def reserve(self, slug):
        try:
            request(f'{self.url}/refs', method='POST', headers=self.headers,
                    body={'ref': 'refs/tags/' + TAG_PREFIX + slug, 'sha': self.revision})
        except HTTPError as error:
            if error.code in (409, 422) and self.exists(slug):
                return False
            raise
        return True

    def release(self, slug):
        request(f'{self.url}/refs/tags/{TAG_PREFIX}{slug}', method='DELETE', headers=self.headers)


def wait_for_article(post, revision):
    url = SITE + post['slug']
    expected = (url, post['title'], post['datePublished'])
    for attempt in range(4):
        try:
            text = request(f'{url}?published={revision}').decode('utf-8')
            schema = re.search(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)
            if schema:
                for item in json.loads(schema.group(1)).get('@graph', []):
                    actual = (item.get('url'), item.get('headline'), item.get('datePublished'))
                    if item.get('@type') == 'BlogPosting' and actual == expected:
                        return
        except (OSError, ValueError):
            pass
        if attempt < 3:
            time.sleep(5)
    raise RuntimeError(f'{post["slug"]} is not yet verifiable on the live website.')


def email_payload(post, *, test=False):
    intro = '<p>这是一封邮件订阅测试，用网站现有文章预览实际收信效果。</p>' if test else ''
    return {
        'subject': 'ethan. 邮件订阅测试' if test else f'ethan. 新文章｜{post["title"]}',
        'slug': ('subscription-test-' if test else 'article-') + post['slug'].removesuffix('.html'),
        'body': (
            '<!-- buttondown-editor-mode: fancy -->'
            f'{intro}<h2>{escape(post["title"])}</h2>'
            f'<p>{escape(post["summary"][:240])}</p>'
            f'<p><a href="{SITE}{post["slug"]}">阅读原文</a></p>'
        ),
        'status': 'draft',
        'canonical_url': SITE + post['slug'],
        'archival_mode': 'disabled',
        'commenting_mode': 'disabled',
        'template': 'modern',
    }


def create_draft(post, api_key, *, test=False):
    identity = ('test:' if test else 'article:') + SITE + post['slug']
    headers = {'Authorization': f'Token {api_key}',
               'X-Idempotency-Key': str(uuid.uuid5(uuid.NAMESPACE_URL, identity))}
    data = json.loads(request(f'{BUTTONDOWN}/emails', method='POST', headers=headers,
                              body=email_payload(post, test=test)))
    email_id = data.get('id', '') if isinstance(data, dict) else ''
    if not isinstance(email_id, str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}', email_id) or data.get('status') != 'draft':
        raise RuntimeError('Buttondown did not return a valid draft. Review the email dashboard.')
    return email_id


def send_test(post, api_key, recipient):
    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', recipient):
        raise ValueError('Specify one valid test recipient using --test-to.')
    wait_for_article(post, 'email-test')
    email_id = create_draft(post, api_key, test=True)
    request(f'{BUTTONDOWN}/emails/{email_id}/send-draft', method='POST',
            headers={'Authorization': f'Token {api_key}'}, body={'recipients': [recipient]})
    print(f'Test preview accepted by Buttondown. Draft ID: {email_id}. Verify receipt in the inbox.')


def notify_new_articles(posts, baseline_slugs, reservations, revision, api_key):
    for post in posts:
        slug = post['slug']
        if slug in baseline_slugs or reservations.exists(slug):
            continue
        wait_for_article(post, revision)
        if not reservations.reserve(slug):
            continue
        try:
            email_id = create_draft(post, api_key)
        except HTTPError as error:
            # Explicit validation/authentication failures cannot have sent an email.
            if error.code in (400, 401, 403, 404, 422):
                reservations.release(slug)
            raise RuntimeError(f'{slug}: Buttondown rejected draft creation (HTTP {error.code}).') from None
        except (OSError, ValueError, RuntimeError):
            raise RuntimeError(f'{slug}: draft creation is uncertain. Check Buttondown before resending.') from None
        try:
            # Publishing is separate from drafting. Test previews only use send-draft.
            data = json.loads(request(
                f'{BUTTONDOWN}/emails/{email_id}/publish', method='POST', body={},
                headers={'Authorization': f'Token {api_key}',
                         'X-Idempotency-Key': str(uuid.uuid5(uuid.NAMESPACE_URL, f'{SITE}{slug}:publish')),
                         'X-Buttondown-Live-Dangerously': 'true'},
            ))
            if not isinstance(data, dict) or data.get('status') not in ('about_to_send', 'scheduled', 'in_flight', 'sent', 'throttled'):
                raise ValueError('Unconfirmed send status')
        except (OSError, ValueError):
            # Keep the claim when the result is unknown, so a rerun cannot duplicate mail.
            raise RuntimeError(f'{slug}: publishing is unconfirmed. Review Buttondown draft {email_id} before resending.') from None
        print(f'{slug}: accepted by Buttondown for delivery (email {email_id}, status {data["status"]}).')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True, encoding='utf-8').strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--test-to', help='Send a draft preview only to this email address.')
    parser.add_argument('--article', default='hello.html', help='Published article to use in the test preview.')
    args = parser.parse_args()
    if args.test_to is not None:
        posts = public_articles(load_articles(ROOT / 'articles.json'))
        post = next((post for post in posts if post['slug'] == args.article), None)
        if post is None:
            raise ValueError('The test article must be publicly published.')
        send_test(post, os.environ['BUTTONDOWN_API_KEY'], args.test_to)
        return
    if os.environ.get('EMAIL_NOTIFY_ENABLED') != 'true':
        print('Email notifications are awaiting activation.')
        return
    if not subscription_username(ROOT):
        raise ValueError('Configure the verified Buttondown username in newsletter.json.')
    revision = os.environ['DEPLOYED_SHA']
    baseline = os.environ.get('EMAIL_NOTIFY_BASE_SHA', '')
    if not re.fullmatch(r'[0-9a-f]{40}', baseline):
        raise ValueError('Set EMAIL_NOTIFY_BASE_SHA to the last commit before subscriptions opened.')
    if git('rev-parse', 'HEAD') != revision:
        raise ValueError('Current checkout does not match the completed deployment.')
    if git('merge-base', baseline, revision) != baseline:
        print('This deployment predates subscription activation.')
        return
    old_posts = validate_articles(json.loads(git('show', f'{baseline}:articles.json')))
    baseline_slugs = {post['slug'] for post in public_articles(old_posts)}
    posts = public_articles(load_articles(ROOT / 'articles.json'))
    reservations = ArticleReservations(os.environ['GITHUB_REPOSITORY'], os.environ['GH_TOKEN'], revision)
    notify_new_articles(reversed(posts), baseline_slugs, reservations, revision, os.environ['BUTTONDOWN_API_KEY'])


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, ValueError) as error:
        sys.exit(str(error))
    except (KeyError, URLError, subprocess.CalledProcessError):
        sys.exit('Email setup or provider request failed. Review the workflow configuration and notification tags.')
