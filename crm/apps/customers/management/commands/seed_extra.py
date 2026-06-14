import random
import uuid
from decimal import Decimal
from datetime import timedelta, date
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from apps.customers.models import Customer, Order
from apps.customers.scoring import RFMScorer

fake = Faker('en_IN')

CITIES = [
    ('Mumbai', 0.22), ('Delhi', 0.18), ('Bangalore', 0.17), ('Chennai', 0.11),
    ('Hyderabad', 0.10), ('Pune', 0.09), ('Kolkata', 0.06), ('Ahmedabad', 0.04),
    ('Jaipur', 0.03),
]
CHANNEL_PREFS = [('whatsapp', 0.45), ('email', 0.30), ('sms', 0.15), ('rcs', 0.10)]
GENDERS = [('male', 0.48), ('female', 0.45), ('other', 0.07)]

CATEGORIES = ['tops', 'bottoms', 'footwear', 'accessories', 'dresses', 'skirts']
PRODUCTS = {
    'tops': ['Cotton Tee', 'Linen Shirt', 'Knit Sweater'],
    'bottoms': ['Slim Jeans', 'Chino Trousers', 'Jogger Pants'],
    'footwear': ['Canvas Sneakers', 'Leather Loafers', 'Ankle Boots'],
    'accessories': ['Tote Bag', 'Leather Belt', 'Silk Scarf'],
    'dresses': ['Wrap Dress', 'Maxi Dress', 'Shift Dress'],
    'skirts': ['Midi Skirt', 'Pleated Skirt', 'Denim Mini Skirt'],
}
PRICES = [499, 799, 1299, 1999, 2499, 3499, 4999]

DEFAULT_COUNT = 308
# Customers are acquired across this many months back from today, so the
# cohort/acquisition charts show a realistic spread instead of one spike.
ACQUISITION_MONTHS = 24


def weighted_choice(pairs):
    items, weights = zip(*pairs)
    return random.choices(items, weights=weights, k=1)[0]


class Command(BaseCommand):
    help = (
        'Add extra realistic customers with acquisition dates and order history '
        'spread across time (default 308 customers over the last 24 months), so '
        'cohort and time-series charts are not clustered on a single date.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=DEFAULT_COUNT,
                            help=f'How many customers to add (default {DEFAULT_COUNT}).')
        parser.add_argument('--months', type=int, default=ACQUISITION_MONTHS,
                            help='Spread acquisition dates across this many months back.')
        parser.add_argument('--force', action='store_true',
                            help='Add customers even if the idempotency guard would skip.')
        parser.add_argument('--skip-if-at-least', dest='skip_if_at_least', type=int, default=400,
                            help='Skip if the customer count is already >= this (default 400).')

    def handle(self, *args, **options):
        count = options['count']
        months = max(1, options['months'])
        now = timezone.now()
        span_days = months * 30

        # Idempotency guard: if the customer base is already at/above the expected
        # post-seed size, assume this has run and skip. Lets the command sit safely
        # in a deploy build without re-adding on every deploy. Use --force to override.
        if not options['force']:
            existing = Customer.objects.count()
            if existing >= options['skip_if_at_least']:
                self.stdout.write(self.style.WARNING(
                    f'{existing} customers already present (>= {options["skip_if_at_least"]}); '
                    f'skipping seed_extra. Use --force to add anyway.'
                ))
                return

        self.stdout.write(f'Creating {count} customers spread across {months} months...')

        created = []          # (customer, created_at) so we can backdate after insert
        for i in range(count):
            phone = '+91' + ''.join(random.choices('0123456789', k=10))
            # Skew acquisitions slightly toward the recent past (more new customers
            # lately) while still covering the full window.
            frac = random.random() ** 1.4  # bias toward smaller = more recent
            days_ago = int(frac * span_days)
            signup = now - timedelta(days=days_ago, hours=random.randint(0, 23))

            dob = fake.date_of_birth(minimum_age=18, maximum_age=65)
            try:
                c = Customer.objects.create(
                    name=fake.name(),
                    email=fake.unique.email(),
                    phone=phone,
                    city=weighted_choice(CITIES),
                    channel_preference=weighted_choice(CHANNEL_PREFS),
                    gender=weighted_choice(GENDERS),
                    date_of_birth=dob,
                    tags=random.sample(['vip', 'newsletter', 'app_user', 'returning'], k=random.randint(0, 2)),
                )
            except Exception:
                continue
            created.append((c, signup))

        # Backdate created_at. auto_now_add forces "now" on insert, so we override
        # it with a queryset .update() (which does not trigger auto_now_add).
        for c, signup in created:
            Customer.objects.filter(pk=c.pk).update(created_at=signup)

        self.stdout.write(f'Created {len(created)} customers. Creating orders...')
        order_count = 0
        for c, signup in created:
            # Orders fall between signup and now, so a customer never orders before
            # they existed — keeps cohort spend coherent over time.
            n_orders = random.randint(0, 6)
            for _ in range(n_orders):
                max_days = max(1, (now - signup).days)
                ordered_at = signup + timedelta(
                    days=random.randint(0, max_days),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59),
                )
                if ordered_at > now:
                    ordered_at = now
                category = random.choice(CATEGORIES)
                product = random.choice(PRODUCTS[category])
                qty = random.randint(1, 3)
                price = random.choice(PRICES)
                Order.objects.create(
                    customer=c,
                    order_number=f'ORD-{uuid.uuid4().hex[:10].upper()}',
                    total_amount=Decimal(str(price)) * qty,
                    status=random.choices(
                        ['placed', 'fulfilled', 'returned', 'cancelled'],
                        weights=[0.1, 0.8, 0.05, 0.05])[0],
                    channel=random.choices(['online', 'app', 'in_store'], weights=[0.6, 0.3, 0.1])[0],
                    product_category=category,
                    items=[{
                        'sku': f'SKU-{random.randint(0, 9999):04d}',
                        'name': product, 'category': category, 'price': price, 'qty': qty,
                    }],
                    ordered_at=ordered_at,
                )
                order_count += 1

        self.stdout.write(f'Created {order_count} orders. Recomputing RFM scores...')
        RFMScorer().compute_all()

        self.stdout.write(self.style.SUCCESS(
            f'Done. Added {len(created)} customers and {order_count} orders '
            f'across {months} months.'
        ))
