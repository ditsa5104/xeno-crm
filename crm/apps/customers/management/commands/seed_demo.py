import random
import uuid
from decimal import Decimal
from datetime import timedelta, date
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

# Non-skirt catalogue used for the general population of orders.
GENERIC_CATEGORIES = ['tops', 'bottoms', 'footwear', 'accessories', 'dresses']
GENERIC_PRODUCTS = {
    'tops': ['Cotton Tee', 'Linen Shirt', 'Knit Sweater'],
    'bottoms': ['Slim Jeans', 'Chino Trousers', 'Jogger Pants'],
    'footwear': ['Canvas Sneakers', 'Leather Loafers', 'Ankle Boots'],
    'accessories': ['Tote Bag', 'Leather Belt', 'Silk Scarf'],
    'dresses': ['Wrap Dress', 'Maxi Dress', 'Shift Dress'],
}
# Skirt catalogue per the spec.
SKIRT_PRODUCTS = ['Midi Skirt', 'Pleated Skirt', 'Denim Mini Skirt']

PRICES = [499, 799, 1299, 1999, 2499, 3499, 4999]

# Demo constants from the spec.
NEW_COLLECTION_NAME = 'Bloom Spring Collection 2026'
NEW_SKIRT_COLLECTION_NAME = 'The Studio Skirt Edit'
BRAND_NAME = 'Plume'

N_CUSTOMERS = 200
N_BIRTHDAY_THIS_MONTH = 30
N_SKIRT_BUYERS = 60


def weighted_choice(pairs):
    items, weights = zip(*pairs)
    return random.choices(items, weights=weights, k=1)[0]


class Command(BaseCommand):
    help = (
        'Seed demo data per the Xeno spec: admin + 200 customers (30 with a '
        'birthday this month, 60 skirt buyers), order history with product '
        'categories, named demo segments, and the two pre-built demo campaigns '
        'with simulated delivery stats.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--fresh', action='store_true',
            help='Delete existing customers/orders/segments/campaigns before seeding.',
        )

    def handle(self, *args, **options):
        if options.get('fresh'):
            self.stdout.write('Clearing existing demo data...')
            from apps.campaigns.models import Campaign, CommunicationLog
            from apps.segments.models import Segment
            CommunicationLog.objects.all().delete()
            Campaign.objects.all().delete()
            Segment.objects.all().delete()
            Order.objects.all().delete()
            Customer.objects.all().delete()
        elif Customer.objects.exists():
            # Idempotency guard: don't re-seed (and double-insert logs) if data
            # is already present. Use --fresh to force a clean reseed.
            self.stdout.write(self.style.WARNING(
                'Customers already exist; skipping seed. Use --fresh to reseed.'
            ))
            return

        self.stdout.write('Creating superuser...')
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@xeno.local', 'admin123')

        customers = self._create_customers()
        self._create_orders(customers)

        self.stdout.write('Computing RFM scores...')
        RFMScorer().compute_all()

        self._create_segments()
        self._create_campaigns()

        self.stdout.write(self.style.SUCCESS('Seed complete.'))

    # ── Customers ────────────────────────────────────────────────────────
    def _create_customers(self):
        self.stdout.write(f'Creating {N_CUSTOMERS} customers...')
        now = timezone.now()
        this_month = now.month
        customers = []
        for i in range(N_CUSTOMERS):
            phone = '+91' + ''.join(random.choices('0123456789', k=10))
            # First N_BIRTHDAY_THIS_MONTH customers get a birthday in the current month.
            if i < N_BIRTHDAY_THIS_MONTH:
                dob = date(
                    random.randint(1975, 2003),
                    this_month,
                    random.randint(1, 28),
                )
            else:
                dob = fake.date_of_birth(minimum_age=18, maximum_age=60)
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
                customers.append(c)
            except Exception:
                continue
        self.stdout.write(f'Created {len(customers)} customers.')
        return customers

    # ── Orders ───────────────────────────────────────────────────────────
    def _create_orders(self, customers):
        self.stdout.write('Creating orders...')
        now = timezone.now()
        # Mark the first N_SKIRT_BUYERS customers as skirt buyers.
        skirt_buyers = set(c.id for c in customers[:N_SKIRT_BUYERS])
        order_count = 0
        for c in customers:
            n_orders = random.randint(1, 5)
            gave_skirt = False
            for j in range(n_orders):
                days_ago = min(int(random.expovariate(1 / 120)), 360)
                ordered_at = now - timedelta(days=days_ago, hours=random.randint(0, 23))

                # Guarantee skirt buyers have at least one recent skirt order.
                if c.id in skirt_buyers and not gave_skirt:
                    category = 'skirts'
                    product = random.choice(SKIRT_PRODUCTS)
                    gave_skirt = True
                    ordered_at = now - timedelta(days=random.randint(5, 300))
                else:
                    category = random.choice(GENERIC_CATEGORIES)
                    product = random.choice(GENERIC_PRODUCTS[category])

                qty = random.randint(1, 2)
                price = random.choice(PRICES)
                total = Decimal(str(price)) * qty
                Order.objects.create(
                    customer=c,
                    order_number=f'ORD-{uuid.uuid4().hex[:10].upper()}',
                    total_amount=total,
                    status=random.choices(
                        ['placed', 'fulfilled', 'returned', 'cancelled'],
                        weights=[0.1, 0.8, 0.05, 0.05])[0],
                    channel=random.choices(['online', 'app', 'in_store'], weights=[0.6, 0.3, 0.1])[0],
                    product_category=category,
                    items=[{
                        'sku': f'SKU-{random.randint(0, 9999):04d}',
                        'name': product,
                        'category': category,
                        'price': price,
                        'qty': qty,
                    }],
                    ordered_at=ordered_at,
                )
                order_count += 1
        self.stdout.write(f'Created {order_count} orders.')

    # ── Segments ─────────────────────────────────────────────────────────
    def _create_segments(self):
        from apps.segments.models import Segment
        from apps.segments.evaluator import SegmentEvaluator
        self.stdout.write('Creating demo segments...')

        Segment.objects.update_or_create(
            name='All Customers',
            defaults=dict(
                description='Every customer in the CRM',
                segment_type='dynamic',
                filter_tree={},
            ),
        )
        Segment.objects.update_or_create(
            name='Skirt Buyers — Last 12 Months',
            defaults=dict(
                description="Customers who purchased any item in the 'Skirts' category in the last 12 months",
                segment_type='dynamic',
                filter_tree={'operator': 'AND', 'conditions': [
                    {'field': 'purchased_category', 'op': 'eq', 'value': 'skirts'},
                ]},
            ),
        )
        Segment.objects.update_or_create(
            name='Birthday This Month',
            defaults=dict(
                description='Customers whose birthday falls in the current calendar month',
                segment_type='dynamic',
                filter_tree={'operator': 'AND', 'conditions': [
                    {'field': 'birthday_month', 'op': 'is_current_month', 'value': True},
                ]},
            ),
        )
        Segment.objects.update_or_create(
            name='High Spenders (Top 20%)',
            defaults=dict(
                description='Customers with total spend over INR 10,000',
                segment_type='dynamic',
                filter_tree={'operator': 'AND', 'conditions': [
                    {'field': 'total_spend', 'op': 'gte', 'value': 10000},
                ]},
            ),
        )

        for seg in Segment.objects.all():
            seg.customer_count = SegmentEvaluator().evaluate(seg.filter_tree).count()
            seg.last_computed = timezone.now()
            seg.save(update_fields=['customer_count', 'last_computed'])

    # ── Campaigns (with simulated delivery stats + logs) ─────────────────
    def _create_campaigns(self):
        from apps.segments.models import Segment
        from apps.segments.evaluator import SegmentEvaluator
        from apps.campaigns.models import Campaign
        self.stdout.write('Creating demo campaigns...')

        birthday_seg = Segment.objects.get(name='Birthday This Month')
        skirt_seg = Segment.objects.get(name='Skirt Buyers — Last 12 Months')

        birthday_template = (
            'Hey {{first_name}}! 🎉\n'
            f'Happy Birthday from all of us at {BRAND_NAME}! 🎂\n\n'
            "It's also our 2nd anniversary — and we're celebrating with you!\n"
            f'As a thank-you for being with us, enjoy 20% OFF our brand new {NEW_COLLECTION_NAME} collection.\n\n'
            'Use code: BDAY2YRS — valid for 48 hours only. 🛍️\n'
            'Shop now → {{cta_link}}'
        )
        skirt_template = (
            'Hi {{first_name}} 👗\n'
            "We noticed you love our skirts — and we think you'll love what's new.\n\n"
            f'Introducing: {NEW_SKIRT_COLLECTION_NAME} — our freshest drop yet. ✨\n'
            'Inspired by your taste, picked just for you.\n\n'
            'Be the first to shop → {{cta_link}}'
        )

        birthday_campaign, _ = Campaign.objects.update_or_create(
            name='Happy Birthday + 2 Years with Us 🎂',
            defaults=dict(
                description="Celebrate the customer's birthday and the brand's 2-year anniversary with a 48h discount.",
                segment=birthday_seg,
                channel='whatsapp',
                message_template=birthday_template,
                send_mode='immediate',
                status='completed',
            ),
        )
        skirt_campaign, _ = Campaign.objects.update_or_create(
            name="New Arrivals: Skirts You'll Love 👗",
            defaults=dict(
                description='Notify past skirt buyers about a new skirt line launch — hyper-personalised.',
                segment=skirt_seg,
                channel='whatsapp',
                message_template=skirt_template,
                send_mode='immediate',
                status='completed',
            ),
        )

        # Simulate delivery funnels per the spec.
        self._simulate_delivery(
            birthday_campaign, birthday_seg,
            delivered_pct=0.85, opened_pct=0.60, clicked_pct=0.25, failed_pct=0.05,
        )
        self._simulate_delivery(
            skirt_campaign, skirt_seg,
            delivered_pct=0.90, opened_pct=0.70, clicked_pct=0.40, failed_pct=0.03,
        )

    def _simulate_delivery(self, campaign, segment, *, delivered_pct, opened_pct, clicked_pct, failed_pct):
        """Create CommunicationLogs with terminal states matching the target funnel."""
        from apps.campaigns.models import CommunicationLog
        from apps.segments.evaluator import SegmentEvaluator
        from apps.campaigns.personaliser import render

        audience = list(SegmentEvaluator().evaluate(segment.filter_tree)[:200])
        n = len(audience)
        if n == 0:
            return

        now = timezone.now()
        launched = now - timedelta(days=1)
        n_failed = int(n * failed_pct)
        n_delivered = int(n * delivered_pct)
        n_opened = int(n * opened_pct)
        n_clicked = int(n * clicked_pct)

        logs = []
        for i, customer in enumerate(audience):
            body = render(campaign.message_template, customer)
            recipient_ok = bool(customer.phone or customer.email)
            log = CommunicationLog(
                campaign=campaign,
                customer=customer,
                channel=campaign.channel,
                message_body=body,
                status='sent',
                queued_at=launched,
                sent_at=launched + timedelta(seconds=2),
            )
            if i < n_failed or not recipient_ok:
                log.status = 'failed'
                log.failure_reason = 'unreachable'
                log.sent_at = None
            elif i < n_clicked:
                log.status = 'clicked'
                log.delivered_at = launched + timedelta(seconds=3)
                log.opened_at = launched + timedelta(seconds=12)
                log.clicked_at = launched + timedelta(seconds=25)
            elif i < n_opened:
                log.status = 'opened'
                log.delivered_at = launched + timedelta(seconds=3)
                log.opened_at = launched + timedelta(seconds=12)
            elif i < n_delivered:
                log.status = 'delivered'
                log.delivered_at = launched + timedelta(seconds=3)
            logs.append(log)

        CommunicationLog.objects.bulk_create(logs, batch_size=200)

        # Roll up stats onto the campaign.
        sent = sum(1 for l in logs if l.status != 'failed')
        campaign.stat_total = n
        campaign.stat_sent = sent
        campaign.stat_failed = sum(1 for l in logs if l.status == 'failed')
        campaign.stat_delivered = sum(1 for l in logs if l.status in ('delivered', 'opened', 'clicked'))
        campaign.stat_opened = sum(1 for l in logs if l.status in ('opened', 'clicked'))
        campaign.stat_clicked = sum(1 for l in logs if l.status == 'clicked')
        campaign.launched_at = launched
        campaign.completed_at = now
        campaign.save(update_fields=[
            'stat_total', 'stat_sent', 'stat_failed', 'stat_delivered',
            'stat_opened', 'stat_clicked', 'launched_at', 'completed_at',
        ])
