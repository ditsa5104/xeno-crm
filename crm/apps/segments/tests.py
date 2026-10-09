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

    def test_segment_and_condition_returns_only_customers_satisfying_all_rules(self):
        # Cause-Effect: AND should require every condition to match.
        tree = {'operator': 'AND', 'conditions': [
            {'field': 'total_spend', 'op': 'gte', 'value': 10000},
            {'field': 'city', 'op': 'eq', 'value': 'Mumbai'},
        ]}
        qs = SegmentEvaluator().evaluate(tree)
        self.assertEqual(set(qs.values_list('id', flat=True)), {self.alice.id})

    def test_segment_and_condition_matches_all_conditions_only(self):
        # Cause-Effect: AND should return only customers satisfying every rule.
        tree = {'operator': 'AND', 'conditions': [
            {'field': 'total_spend', 'op': 'gte', 'value': 10000},
            {'field': 'city', 'op': 'eq', 'value': 'Mumbai'},
        ]}
        qs = SegmentEvaluator().evaluate(tree)
        self.assertEqual(set(qs.values_list('id', flat=True)), {self.alice.id})

    def test_segment_or_condition_returns_customers_matching_any_rule(self):
        # Decision table: OR should include customers matching any branch.
        tree = {'operator': 'OR', 'conditions': [
            {'field': 'city', 'op': 'eq', 'value': 'Mumbai'},
            {'field': 'city', 'op': 'eq', 'value': 'Delhi'},
        ]}
        qs = SegmentEvaluator().evaluate(tree)
        self.assertEqual(set(qs.values_list('id', flat=True)), {self.alice.id, self.bob.id})

    def test_segment_or_condition_returns_customers_satisfying_any_condition(self):
        # Decision table: OR should match any condition in the segment tree.
        tree = {'operator': 'OR', 'conditions': [
            {'field': 'city', 'op': 'eq', 'value': 'Mumbai'},
            {'field': 'city', 'op': 'eq', 'value': 'Delhi'},
        ]}
        qs = SegmentEvaluator().evaluate(tree)
        self.assertEqual(set(qs.values_list('id', flat=True)), {self.alice.id, self.bob.id})

    def test_unknown_segment_field_raises_expected_value_error(self):
        # Unit testing: unsupported field names should be rejected.
        with self.assertRaises(ValueError):
            SegmentEvaluator().evaluate({'operator': 'AND', 'conditions': [
                {'field': 'foo', 'op': 'eq', 'value': 'x'}
            ]})

    def test_invalid_segment_field_raises_expected_error(self):
        # Unit testing: invalid/unknown segment fields should raise the expected error.
        with self.assertRaises(ValueError):
            SegmentEvaluator().evaluate({'operator': 'AND', 'conditions': [
                {'field': 'wrong_field', 'op': 'eq', 'value': 'value'}
            ]})

    def test_unknown_field_raises(self):
        with self.assertRaises(ValueError):
            SegmentEvaluator().evaluate({'operator': 'AND', 'conditions': [
                {'field': 'foo', 'op': 'eq', 'value': 'x'}
            ]})
