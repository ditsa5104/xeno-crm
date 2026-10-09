from decimal import Decimal
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from apps.segments.evaluator import SegmentEvaluator
from .models import Customer, Order
from .scoring import RFMScorer


class RFMTests(TestCase):
    def test_valid_customer_creation(self):
        customer = Customer.objects.create(
            name="Alice",
            email="alice@example.com",
            phone="+919876543210",
            city="Mumbai",
        )

        self.assertIsNotNone(customer.id)
        self.assertEqual(customer.name, "Alice")
        self.assertEqual(customer.email, "alice@example.com")
        self.assertEqual(customer.phone, "+919876543210")
        self.assertEqual(customer.city, "Mumbai")

    def test_customer_creation_valid_data_creates_record_and_persists_expected_values(self):
        # Unit testing: valid customer creation, success check, and persisted values.
        customer = Customer.objects.create(
            name='Alice Example',
            email='alice@example.com',
            phone='+919999999999',
            city='Bengaluru',
        )

        self.assertIsNotNone(customer.pk)
        self.assertTrue(Customer.objects.filter(pk=customer.pk).exists())
        self.assertEqual(customer.name, 'Alice Example')
        self.assertEqual(customer.email, 'alice@example.com')
        self.assertEqual(customer.phone, '+919999999999')
        self.assertEqual(customer.city, 'Bengaluru')

    def test_invalid_customer_data_is_rejected_by_model_validation(self):
        # Unit testing: name/email validation should reject invalid input.
        invalid_email = Customer(
            name='Bad Email',
            email='not-an-email',
            phone='+919876543210',
            city='Delhi',
        )
        with self.assertRaises(ValidationError):
            invalid_email.full_clean()

        missing_name = Customer(
            email='valid@example.com',
            phone='+919876543211',
            city='Delhi',
        )
        with self.assertRaises(ValidationError):
            missing_name.full_clean()

    def test_total_spend_bva_uses_project_threshold_for_boundary_values(self):
        # BVA: values immediately below, at, and above the real project threshold for spend.
        threshold = Decimal('10000')
        below = Customer.objects.create(
            name='Below', email='below@example.com', total_spend=threshold - Decimal('1')
        )
        at = Customer.objects.create(
            name='At', email='at@example.com', total_spend=threshold
        )
        above = Customer.objects.create(
            name='Above', email='above@example.com', total_spend=threshold + Decimal('1')
        )

        tree = {'operator': 'AND', 'conditions': [{'field': 'total_spend', 'op': 'gte', 'value': 10000}]}
        qs = SegmentEvaluator().evaluate(tree)

        self.assertNotIn(below, qs)
        self.assertIn(at, qs)
        self.assertIn(above, qs)

    def test_quintile_rank(self):
        ranks = RFMScorer._quintile_rank([10, 20, 30, 40, 50])
        self.assertEqual(ranks[10], 1)
        self.assertEqual(ranks[50], 5)

    def test_compute_all_skips_empty(self):
        n = RFMScorer().compute_all()
        self.assertEqual(n, 0)

    def test_signal_updates_stats(self):
        c = Customer.objects.create(name='Test', email='t@x.com', phone='+911')
        Order.objects.create(
            customer=c, order_number='O1', total_amount=Decimal('500'),
            status='fulfilled', ordered_at=timezone.now(),
        )
        c.refresh_from_db()
        self.assertEqual(c.total_orders, 1)
        self.assertEqual(c.total_spend, Decimal('500'))
