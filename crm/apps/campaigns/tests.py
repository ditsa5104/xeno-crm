from django.test import TestCase
from apps.customers.models import Customer
from .personaliser import render


class PersonaliserTests(TestCase):
    def test_basic_render(self):
        c = Customer.objects.create(name='Alice', email='a@x.com', city='Mumbai')
        out = render('Hi {{name}} from {{city}}!', c)
        self.assertEqual(out, 'Hi Alice from Mumbai!')

    def test_unknown_tag_preserved(self):
        c = Customer.objects.create(name='Bob', email='b@x.com')
        out = render('Hi {{name}} {{foo}}', c)
        self.assertIn('{{foo}}', out)
