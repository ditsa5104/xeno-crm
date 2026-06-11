from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from .models import Customer, Order
from .scoring import RFMScorer


class RFMTests(TestCase):
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
