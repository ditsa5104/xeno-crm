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
