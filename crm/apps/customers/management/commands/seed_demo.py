import random
import uuid
from decimal import Decimal
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker import Faker

from apps.customers.models import Customer, Order
from apps.customers.scoring import RFMScorer

User = get_user_model()
fake = Faker('en_IN')

CITIES = [
    ('Mumbai', 0.25), ('Delhi', 0.20), ('Bangalore', 0.18), ('Chennai', 0.12),
    ('Hyderabad', 0.10), ('Pune', 0.08), ('Kolkata', 0.04), ('Ahmedabad', 0.03),
]
CHANNEL_PREFS = [('whatsapp', 0.45), ('email', 0.30), ('sms', 0.15), ('rcs', 0.10)]
GENDERS = [('male', 0.48), ('female', 0.45), ('other', 0.07)]

CATEGORIES = ['tops', 'bottoms', 'footwear', 'accessories']
SKUS = [
    {'sku': f'SKU-{i:04d}', 'name': fake.color_name() + ' ' + random.choice(['Tee', 'Jeans', 'Sneakers', 'Bag', 'Watch']),
     'category': random.choice(CATEGORIES), 'price': random.choice([499, 799, 1299, 1999, 2499, 3499, 4999])}
    for i in range(20)
]


def weighted_choice(pairs):
    items, weights = zip(*pairs)
    return random.choices(items, weights=weights, k=1)[0]


class Command(BaseCommand):
    help = 'Seed demo data: 1 admin, 150 customers, ~5 orders/customer, demo segments and campaigns.'

    def handle(self, *args, **options):
        self.stdout.write('Creating superuser...')
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@xeno.local', 'admin123')

        self.stdout.write('Creating customers...')
        customers = []
        for _ in range(150):
            phone = '+91' + ''.join(random.choices('0123456789', k=10))
            try:
                c = Customer.objects.create(
                    name=fake.name(),
                    email=fake.unique.email(),
                    phone=phone,
                    city=weighted_choice(CITIES),
                    channel_preference=weighted_choice(CHANNEL_PREFS),
                    gender=weighted_choice(GENDERS),
                    tags=random.sample(['vip', 'newsletter', 'app_user', 'returning'], k=random.randint(0, 2)),
                )
                customers.append(c)
            except Exception:
                continue

        self.stdout.write(f'Created {len(customers)} customers. Creating orders...')
        now = timezone.now()
        order_count = 0
        for c in customers:
            n_orders = random.randint(2, 10)
            for _ in range(n_orders):
                days_ago = int(random.expovariate(1 / 120))  # long-tail
                days_ago = min(days_ago, 540)
                ordered_at = now - timedelta(days=days_ago, hours=random.randint(0, 23))
                items = []
                for _ in range(random.randint(1, 3)):
                    s = random.choice(SKUS)
                    items.append({**s, 'qty': random.randint(1, 2)})
                total = sum(Decimal(str(it['price'])) * it['qty'] for it in items)
                Order.objects.create(
                    customer=c,
                    order_number=f'ORD-{uuid.uuid4().hex[:10].upper()}',
                    total_amount=total,
                    status=random.choices(['placed', 'fulfilled', 'returned', 'cancelled'], weights=[0.1, 0.8, 0.05, 0.05])[0],
                    channel=random.choices(['online', 'app', 'in_store'], weights=[0.6, 0.3, 0.1])[0],
                    items=items,
                    ordered_at=ordered_at,
                )
                order_count += 1

        self.stdout.write(f'Created {order_count} orders. Computing RFM scores...')
        RFMScorer().compute_all()

        # Demo segments
        from apps.segments.models import Segment
        self.stdout.write('Creating demo segments...')
        Segment.objects.update_or_create(
            name='High Value Customers',
            defaults=dict(
                description='Customers with total spend over INR 10,000',
                segment_type='dynamic',
                filter_tree={'operator': 'AND', 'conditions': [{'field': 'total_spend', 'op': 'gte', 'value': 10000}]},
            ),
        )
        Segment.objects.update_or_create(
            name='At Risk Customers',
            defaults=dict(
                description='Loyal customers who have not ordered in 90+ days',
                segment_type='dynamic',
                filter_tree={'operator': 'AND', 'conditions': [
                    {'field': 'last_order_at', 'op': 'days_ago_gte', 'value': 90},
                    {'field': 'rfm_frequency_score', 'op': 'gte', 'value': 3},
                ]},
            ),
        )
        Segment.objects.update_or_create(
            name='Mumbai Shoppers',
            defaults=dict(
                description='Customers based in Mumbai',
                segment_type='dynamic',
                filter_tree={'operator': 'AND', 'conditions': [{'field': 'city', 'op': 'eq', 'value': 'Mumbai'}]},
            ),
        )

        from apps.segments.evaluator import SegmentEvaluator
        for seg in Segment.objects.all():
            seg.customer_count = SegmentEvaluator().evaluate(seg.filter_tree).count()
            seg.last_computed = timezone.now()
            seg.save()

        # Demo draft campaigns
        from apps.campaigns.models import Campaign
        hv = Segment.objects.get(name='High Value Customers')
        ar = Segment.objects.get(name='At Risk Customers')
        Campaign.objects.update_or_create(
            name='VIP Spring Drop',
            defaults=dict(
                description='Early access for high-value customers',
                segment=hv,
                channel='whatsapp',
                message_template='Hi {{name}}, our spring drop is live for VIPs in {{city}}! Enjoy 20% off — link inside.',
                status='draft',
            ),
        )
        Campaign.objects.update_or_create(
            name='We Miss You',
            defaults=dict(
                description='Win-back campaign for at-risk customers',
                segment=ar,
                channel='email',
                message_template='Subject: We miss you, {{name}}!\nIt has been a while. Here is a 15% off code just for you. Visit us soon.',
                status='draft',
            ),
        )

        self.stdout.write(self.style.SUCCESS('Seed complete.'))
