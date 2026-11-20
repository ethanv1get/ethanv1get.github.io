"""Exercise send failures, reruns and test isolation without contacting providers."""
import json
from unittest import TestCase, main
from unittest.mock import Mock, patch
from urllib.error import HTTPError

import notify_email as notice
from content import public_articles


class NotificationTests(TestCase):
    def setUp(self):
        self.post = {'slug': 'new-note.html', 'title': '新文章 <测试>', 'summary': '测试 & 摘要',
                     'draft': False, 'datePublished': '2026-11-19'}
        self.claimed = set()
        self.reservations = Mock()
        self.reservations.exists.side_effect = self.claimed.__contains__
        self.reservations.reserve.side_effect = self.reserve
        self.reservations.release.side_effect = self.claimed.remove

    def reserve(self, slug):
        if slug in self.claimed:
            return False
        self.claimed.add(slug)
        return True

    def run_notifications(self):
        records = [self.post, {**self.post, 'slug': 'old-note.html'},
                   {**self.post, 'slug': 'draft.html', 'draft': True}]
        notice.notify_new_articles(public_articles(records), {'old-note.html'}, self.reservations,
                                   'a' * 40, 'fixture-key')

    @patch.object(notice, 'wait_for_article')
    @patch.object(notice, 'request', side_effect=[b'{"id":"em_fixture","status":"draft"}',
                                                b'{"id":"em_fixture","status":"about_to_send"}'])
    def test_edits_old_articles_drafts_and_reruns_do_not_duplicate_notifications(self, request, verify):
        self.run_notifications()
        self.run_notifications()
        verify.assert_called_once_with(self.post, 'a' * 40)
        self.assertEqual(request.call_count, 2)
        create = request.call_args_list[0]
        payload = create.kwargs['body']
        self.assertEqual(payload['status'], 'draft')
        self.assertEqual(payload['archival_mode'], 'disabled')
        self.assertIn('https://ethanv1.top/new-note.html', payload['body'])
        self.assertIn('新文章 &lt;测试&gt;', payload['body'])
        self.assertIn('测试 &amp; 摘要', payload['body'])
        publish = request.call_args_list[1]
        self.assertEqual(publish.args[0], notice.BUTTONDOWN + '/emails/em_fixture/publish')
        self.assertNotEqual(create.kwargs['headers']['X-Idempotency-Key'],
                            publish.kwargs['headers']['X-Idempotency-Key'])

    @patch.object(notice, 'wait_for_article')
    @patch.object(notice, 'request', side_effect=[b'{"id":"em_fixture","status":"draft"}',
                                                b'{"id":"em_fixture","status":"scheduled"}'])
    def test_provider_scheduled_acceptance_succeeds_without_duplicate_send(self, request, verify):
        self.run_notifications()
        self.run_notifications()
        self.assertEqual(request.call_count, 2)
        self.assertEqual(self.claimed, {'new-note.html'})

    @patch.object(notice, 'wait_for_article')
    @patch.object(notice, 'request', side_effect=[b'{"id":"em_fixture","status":"draft"}',
                                                b'{"id":"em_fixture","status":"draft"}'])
    def test_unconfirmed_status_keeps_claim_and_does_not_send_twice(self, request, verify):
        with self.assertRaisesRegex(RuntimeError, 'publishing is unconfirmed'):
            self.run_notifications()
        self.run_notifications()
        self.assertEqual(request.call_count, 2)
        self.assertEqual(self.claimed, {'new-note.html'})

    @patch.object(notice, 'wait_for_article', side_effect=RuntimeError('Article is not online'))
    @patch.object(notice, 'request')
    def test_unavailable_article_does_not_claim_or_send(self, request, verify):
        with self.assertRaisesRegex(RuntimeError, 'not online'):
            self.run_notifications()
        self.assertEqual(self.claimed, set())
        request.assert_not_called()

    @patch.object(notice, 'wait_for_article')
    @patch.object(notice, 'request', side_effect=[b'{"id":"em_fixture","status":"draft"}', TimeoutError])
    def test_timeout_after_publishing_cannot_trigger_another_send(self, request, verify):
        with self.assertRaisesRegex(RuntimeError, 'publishing is unconfirmed'):
            self.run_notifications()
        self.run_notifications()
        self.assertEqual(request.call_count, 2)
        self.assertEqual(self.claimed, {'new-note.html'})

    @patch.object(notice, 'wait_for_article')
    @patch.object(notice, 'request', side_effect=TimeoutError)
    def test_timeout_creating_draft_keeps_claim_for_provider_reconciliation(self, request, verify):
        with self.assertRaisesRegex(RuntimeError, 'draft creation is uncertain'):
            self.run_notifications()
        self.run_notifications()
        request.assert_called_once()
        self.assertEqual(self.claimed, {'new-note.html'})

    @patch.object(notice, 'wait_for_article')
    @patch.object(notice, 'request', side_effect=HTTPError(None, 403, 'Account under review', None, None))
    def test_draft_rejection_before_sending_can_be_retried(self, request, verify):
        with self.assertRaisesRegex(RuntimeError, '403'):
            self.run_notifications()
        self.assertEqual(self.claimed, set())

    @patch.object(notice, 'request')
    def test_live_article_metadata_matches_published_record(self, request):
        schema = {'@graph': [{'@type': 'BlogPosting', 'url': notice.SITE + self.post['slug'],
                              'headline': self.post['title'], 'datePublished': self.post['datePublished']}]}
        request.return_value = ('<head><script type="application/ld+json">' + json.dumps(schema)
                                + '</script></head>').encode()
        notice.wait_for_article(self.post, 'a' * 40)
        request.assert_called_once()

    @patch.object(notice, 'request')
    def test_overlapping_workflows_reserve_an_article_once(self, request):
        ref = 'refs/tags/email-notified/new-note.html'
        request.side_effect = [HTTPError(None, 422, 'Ref already exists', None, None),
                               json.dumps({'ref': ref}).encode()]
        reservations = notice.ArticleReservations('example/site', 'fixture-token', 'a' * 40)
        self.assertFalse(reservations.reserve('new-note.html'))

    @patch.object(notice, 'wait_for_article')
    @patch.object(notice, 'request', side_effect=[b'{"id":"em_test","status":"draft"}', b'{}'])
    def test_test_preview_only_targets_one_address_without_publishing(self, request, verify):
        notice.send_test(self.post, 'fixture-key', 'reader@example.com')
        self.assertEqual(request.call_count, 2)
        create, preview = request.call_args_list
        self.assertEqual(create.kwargs['body']['status'], 'draft')
        self.assertIn('测试', create.kwargs['body']['subject'])
        self.assertEqual(preview.args[0], notice.BUTTONDOWN + '/emails/em_test/send-draft')
        self.assertEqual(preview.kwargs['body'], {'recipients': ['reader@example.com']})
        self.assertEqual(self.claimed, set())

    @patch.object(notice, 'request')
    def test_invalid_test_recipient_never_calls_provider(self, request):
        with self.assertRaises(ValueError):
            notice.send_test(self.post, 'fixture-key', 'first@example.com,second@example.com')
        request.assert_not_called()


if __name__ == '__main__':
    main()
