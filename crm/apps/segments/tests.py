from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from apps.customers.models import Customer, Order
from .evaluator import SegmentEvaluator


class SegmentEvaluatorTests(TestCase):
    def setUp(self):
        self.alice = Customer.objects.create(name='Alice', email='a@x.com', city='Mumbai')
        self.bob = Customer.objects.create(name='Bob', email='b@x.com', city='Delhi')
        Order.objects.create(
            customer=self.alice, order_number='O1', total_amount=Decimal('15000'),
            status='fulfilled', ordered_at=timezone.now() - timedelta(days=10),
        )
        Order.objects.create(
            customer=self.bob, order_number='O2', total_amount=Decimal('500'),
            status='fulfilled', ordered_at=timezone.now() - timedelta(days=200),
        )

    def test_simple_and(self):
        tree = {'operator': 'AND', 'conditions': [
            {'field': 'total_spend', 'op': 'gte', 'value': 10000},
            {'field': 'city', 'op': 'eq', 'value': 'Mumbai'},
        ]}
        qs = SegmentEvaluator().evaluate(tree)
        self.assertEqual(set(qs.values_list('id', flat=True)), {self.alice.id})

    def test_or(self):
        tree = {'operator': 'OR', 'conditions': [
            {'field': 'city', 'op': 'eq', 'value': 'Mumbai'},
            {'field': 'city', 'op': 'eq', 'value': 'Delhi'},
        ]}
        qs = SegmentEvaluator().evaluate(tree)
        self.assertEqual(qs.count(), 2)

    def test_days_ago(self):
        tree = {'operator': 'AND', 'conditions': [
            {'field': 'last_order_at', 'op': 'days_ago_lte', 'value': 30},
        ]}
        qs = SegmentEvaluator().evaluate(tree)
        self.assertIn(self.alice, qs)
        self.assertNotIn(self.bob, qs)

    def test_unknown_field_raises(self):
        with self.assertRaises(ValueError):
            SegmentEvaluator().evaluate({'operator': 'AND', 'conditions': [
                {'field': 'foo', 'op': 'eq', 'value': 'x'}
            ]})
