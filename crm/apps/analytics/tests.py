from django.test import TestCase
from .aggregators import dashboard_summary


class AggregatorTests(TestCase):
    def test_dashboard_summary_runs(self):
        out = dashboard_summary()
        self.assertIn('total_customers', out)
