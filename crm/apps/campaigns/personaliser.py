import re
from decimal import Decimal


MERGE_TAG_RE = re.compile(r'\{\{\s*(\w+)\s*\}\}')


def render(template: str, customer, extra: dict | None = None) -> str:
    extra = extra or {}
    last_order = customer.orders.order_by('-ordered_at').first() if hasattr(customer, 'orders') else None
    ctx = {
        'name': customer.name or '',
        'first_name': (customer.name or '').split(' ')[0],
        'city': customer.city or '',
        'email': customer.email or '',
        'phone': customer.phone or '',
        'last_order_amount': str(last_order.total_amount) if last_order else '',
        'rfm_tier': customer.rfm_tier,
        'total_spend': str(customer.total_spend),
        **extra,
    }

    def repl(m):
        return str(ctx.get(m.group(1), m.group(0)))

    return MERGE_TAG_RE.sub(repl, template)
