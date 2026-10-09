import json
from django.test import TestCase, Client
from django.utils import timezone
from apps.core.utils import hmac_sign
from apps.customers.models import Customer
from apps.segments.models import Segment
from apps.campaigns.models import Campaign, CommunicationLog
from .state_machine import CommunicationStateMachine


class StateMachineTests(TestCase):
    def test_valid_transitions(self):
        self.assertTrue(CommunicationStateMachine.can_transition('queued', 'sent'))
        self.assertTrue(CommunicationStateMachine.can_transition('sent', 'delivered'))
        self.assertFalse(CommunicationStateMachine.can_transition('delivered', 'sent'))
        self.assertFalse(CommunicationStateMachine.can_transition('clicked', 'sent'))

    def _log(self):
        c = Customer.objects.create(name='Y', email='y@y.com')
        s = Segment.objects.create(name='s2', filter_tree={'operator': 'AND', 'conditions': []})
        camp = Campaign.objects.create(name='c2', segment=s, channel='whatsapp', message_template='hi')
        return CommunicationLog.objects.create(
            campaign=camp, customer=c, channel='whatsapp', message_body='hi', status='queued',
        )

    def test_out_of_order_events_are_recorded(self):
        """A 'clicked' arriving before 'opened'/'delivered' must not be dropped."""
        log = self._log()
        now = timezone.now()
        # Clicked arrives first (reordered).
        self.assertTrue(CommunicationStateMachine.apply(log, 'clicked', now, {}))
        self.assertEqual(log.status, 'clicked')
        # Delivered arrives later — still recorded, status stays at furthest stage.
        self.assertTrue(CommunicationStateMachine.apply(log, 'delivered', now, {}))
        self.assertIsNotNone(log.delivered_at)
        self.assertEqual(log.status, 'clicked')
        # Opened arrives last — recorded too.
        self.assertTrue(CommunicationStateMachine.apply(log, 'opened', now, {}))
        self.assertIsNotNone(log.opened_at)
        self.assertEqual(log.status, 'clicked')

    def test_duplicate_event_is_ignored(self):
        log = self._log()
        now = timezone.now()
        self.assertTrue(CommunicationStateMachine.apply(log, 'delivered', now, {}))
        self.assertFalse(CommunicationStateMachine.apply(log, 'delivered', now, {}))

    def test_valid_communication_state_transition_updates_status(self):
        # Unit testing: queued -> sent -> delivered is a valid progression.
        log = self._log()
        now = timezone.now()
        self.assertTrue(CommunicationStateMachine.apply(log, 'sent', now, {}))
        self.assertEqual(log.status, 'sent')
        self.assertTrue(CommunicationStateMachine.apply(log, 'delivered', now, {}))
        self.assertEqual(log.status, 'delivered')
        self.assertIsNotNone(log.delivered_at)

    def test_valid_communication_state_transition_queued_to_delivered_updates_status(self):
        # Unit testing: a valid queued -> sent -> delivered transition should update status correctly.
        log = self._log()
        now = timezone.now()
        self.assertTrue(CommunicationStateMachine.apply(log, 'sent', now, {}))
        self.assertEqual(log.status, 'sent')
        self.assertTrue(CommunicationStateMachine.apply(log, 'delivered', now, {}))
        self.assertEqual(log.status, 'delivered')
        self.assertIsNotNone(log.delivered_at)

    def test_duplicate_communication_event_is_ignored_for_same_stage(self):
        # Cause-Effect: duplicate callback should not advance or double-count state.
        log = self._log()
        now = timezone.now()
        self.assertTrue(CommunicationStateMachine.apply(log, 'sent', now, {}))
        self.assertFalse(CommunicationStateMachine.apply(log, 'sent', now, {}))
        self.assertEqual(log.status, 'sent')

    def test_duplicate_communication_event_is_ignored_without_state_change(self):
        # Cause-Effect: applying the same event twice should be ignored and not change the status.
        log = self._log()
        now = timezone.now()
        self.assertTrue(CommunicationStateMachine.apply(log, 'delivered', now, {}))
        self.assertFalse(CommunicationStateMachine.apply(log, 'delivered', now, {}))
        self.assertEqual(log.status, 'delivered')

    def test_failed_after_success_is_ignored(self):
        log = self._log()
        now = timezone.now()
        self.assertTrue(CommunicationStateMachine.apply(log, 'delivered', now, {}))
        # A stale 'failed' must not override a delivered message.
        self.assertFalse(CommunicationStateMachine.apply(log, 'failed', now, {'reason': 'network_timeout'}))
        self.assertEqual(log.status, 'delivered')

    def test_success_after_failed_recovers(self):
        log = self._log()
        now = timezone.now()
        self.assertTrue(CommunicationStateMachine.apply(log, 'failed', now, {'reason': 'network_timeout'}))
        self.assertEqual(log.status, 'failed')
        # If a delivered callback then arrives, the message did get through.
        self.assertTrue(CommunicationStateMachine.apply(log, 'delivered', now, {}))
        self.assertEqual(log.status, 'delivered')
        self.assertEqual(log.failure_reason, '')


class WebhookHMACTests(TestCase):
    def setUp(self):
        self.client = Client()
        c = Customer.objects.create(name='X', email='x@x.com')
        s = Segment.objects.create(name='all', filter_tree={'operator': 'AND', 'conditions': []})
        camp = Campaign.objects.create(name='c', segment=s, channel='email', message_template='hi')
        self.log = CommunicationLog.objects.create(
            campaign=camp, customer=c, channel='email', message_body='hi', status='queued',
        )

    def test_invalid_signature(self):
        body = json.dumps({'message_id': str(self.log.id), 'event_type': 'sent'})
        resp = self.client.post(
            '/api/v1/webhooks/channel-event/',
            data=body,
            content_type='application/json',
            HTTP_X_XENO_SIGNATURE='bogus',
        )
        self.assertEqual(resp.status_code, 401)

    def test_invalid_webhook_signature_is_rejected_with_401(self):
        # Integration testing: invalid HMAC signature must be rejected.
        body = json.dumps({'message_id': str(self.log.id), 'event_type': 'sent'})
        resp = self.client.post(
            '/api/v1/webhooks/channel-event/',
            data=body,
            content_type='application/json',
            HTTP_X_XENO_SIGNATURE='bogus',
        )
        self.assertEqual(resp.status_code, 401)

    def test_invalid_webhook_signature_returns_401_for_rejected_request(self):
        # Integration testing: a bad signature should be rejected with HTTP 401.
        body = json.dumps({'message_id': str(self.log.id), 'event_type': 'sent'})
        resp = self.client.post(
            '/api/v1/webhooks/channel-event/',
            data=body,
            content_type='application/json',
            HTTP_X_XENO_SIGNATURE='bogus-signature',
        )
        self.assertEqual(resp.status_code, 401)

    def test_valid_signature_advances_status(self):
        body = json.dumps({
            'message_id': str(self.log.id),
            'event_type': 'sent',
            'occurred_at': timezone.now().isoformat(),
        })
        sig = hmac_sign(body.encode())
        resp = self.client.post(
            '/api/v1/webhooks/channel-event/',
            data=body,
            content_type='application/json',
            HTTP_X_XENO_SIGNATURE=sig,
        )
        self.assertEqual(resp.status_code, 200)
        self.log.refresh_from_db()
        self.assertEqual(self.log.status, 'sent')

    def test_valid_webhook_signature_is_accepted_and_updates_status(self):
        # Integration testing: a valid signed callback should pass validation and update state.
        body = json.dumps({
            'message_id': str(self.log.id),
            'event_type': 'delivered',
            'occurred_at': timezone.now().isoformat(),
        })
        sig = hmac_sign(body.encode())
        resp = self.client.post(
            '/api/v1/webhooks/channel-event/',
            data=body,
            content_type='application/json',
            HTTP_X_XENO_SIGNATURE=sig,
        )
        self.assertEqual(resp.status_code, 200)
        self.log.refresh_from_db()
        self.assertEqual(self.log.status, 'delivered')

    def test_valid_webhook_signature_accepts_request_and_updates_communication_status(self):
        # Integration testing: correctly signed requests must be accepted and update state.
        body = json.dumps({
            'message_id': str(self.log.id),
            'event_type': 'sent',
            'occurred_at': timezone.now().isoformat(),
        })
        sig = hmac_sign(body.encode())
        resp = self.client.post(
            '/api/v1/webhooks/channel-event/',
            data=body,
            content_type='application/json',
            HTTP_X_XENO_SIGNATURE=sig,
        )
        self.assertEqual(resp.status_code, 200)
        self.log.refresh_from_db()
        self.assertEqual(self.log.status, 'sent')
