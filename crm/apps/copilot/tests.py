from django.test import TestCase
from apps.customers.models import Customer
from .tools import get_customer_summary, get_dashboard_summary


class ToolTests(TestCase):
    def test_get_customer_summary_not_found(self):
        out = get_customer_summary(customer_identifier='no-such-customer')
        self.assertIn('error', out)

    def test_get_customer_summary_found(self):
        Customer.objects.create(name='Alice', email='a@x.com')
        out = get_customer_summary(customer_identifier='alice')
        self.assertEqual(out['name'], 'Alice')

    def test_dashboard_summary(self):
        out = get_dashboard_summary()
        self.assertIn('total_customers', out)
