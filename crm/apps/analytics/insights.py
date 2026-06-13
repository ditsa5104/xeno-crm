"""AI-native action insights.

These power the contextual "do this now" buttons across the CRM (e.g. "Who do I
talk to today"). Each insight is a deterministic, data-grounded recommendation
built from RFM/churn/LTV signals — fast and explainable. An optional AI layer
(see views) turns the structured result into a short natural-language playbook,
but the recommendations themselves never depend on the LLM being available.
"""
from datetime import timedelta
from django.db.models import Count
from django.utils import timezone

from apps.customers.models import Customer


def _customer_brief(c, reason):
    return {
        'id': str(c.id),
        'name': c.name,
        'email': c.email,
        'phone': c.phone,
        'city': c.city,
        'rfm_tier': c.rfm_tier,
        'churn_risk_score': c.churn_risk_score,
        'total_spend': float(c.total_spend),
        'total_orders': c.total_orders,
        'ltv_estimate': float(c.ltv_estimate),
        'last_order_at': c.last_order_at.isoformat() if c.last_order_at else None,
        'channel_preference': c.channel_preference,
        'reason': reason,
    }


def who_to_contact_today(limit=10):
    """High-value customers slipping away: strong RFM history but rising churn risk.

    Ranks by (LTV at stake x churn risk) so the marketer spends attention where
    losing the customer hurts most and the window is closing.
    """
    candidates = (
        Customer.objects
        .filter(total_orders__gt=0, churn_risk_score__gte=0.5)
        .exclude(rfm_tier__in=['Lost'])
        .order_by('-churn_risk_score')[:300]
    )
    scored = []
    for c in candidates:
        value_at_risk = float(c.ltv_estimate or 0) * float(c.churn_risk_score or 0)
        days = (timezone.now() - c.last_order_at).days if c.last_order_at else None
        reason = (
            f"{c.rfm_tier} · {int((c.churn_risk_score or 0) * 100)}% churn risk"
            + (f" · last order {days}d ago" if days is not None else "")
        )
        scored.append((value_at_risk, c, reason))
    scored.sort(key=lambda x: -x[0])
    return {
        'title': 'Who to talk to today',
        'subtitle': 'High-value customers at rising risk of churning — reach out before you lose them.',
        'customers': [_customer_brief(c, r) for _, c, r in scored[:limit]],
    }


def win_back_candidates(limit=10):
    """Lapsed customers who were once valuable — prime for a win-back offer."""
    cutoff = timezone.now() - timedelta(days=90)
    qs = (
        Customer.objects
        .filter(total_orders__gte=2, last_order_at__lt=cutoff)
        .order_by('-total_spend')[:limit]
    )
    out = []
    for c in qs:
        days = (timezone.now() - c.last_order_at).days if c.last_order_at else None
        out.append(_customer_brief(c, f"₹{int(c.total_spend)} lifetime · dormant {days}d"))
    return {
        'title': 'Win back lapsed customers',
        'subtitle': "Customers who used to buy regularly but have gone quiet for 90+ days.",
        'customers': out,
    }


def vip_to_reward(limit=10):
    """Top-tier customers worth a loyalty/thank-you gesture."""
    qs = (
        Customer.objects
        .filter(rfm_tier__in=['Champions', 'Loyal'])
        .order_by('-rfm_composite', '-total_spend')[:limit]
    )
    out = [_customer_brief(c, f"{c.rfm_tier} · ₹{int(c.total_spend)} · {c.total_orders} orders") for c in qs]
    return {
        'title': 'Reward your VIPs',
        'subtitle': 'Your most valuable, most loyal customers — worth a thank-you or early access.',
        'customers': out,
    }


def rising_customers(limit=10):
    """Recent customers with momentum — nudge them toward loyalty."""
    qs = (
        Customer.objects
        .filter(rfm_tier__in=['Recent Customers', 'Potential Loyalists'])
        .order_by('-rfm_composite')[:limit]
    )
    out = [_customer_brief(c, f"{c.rfm_tier} · {c.total_orders} orders so far") for c in qs]
    return {
        'title': 'Grow rising customers',
        'subtitle': 'Newer customers showing momentum — the right nudge turns them into regulars.',
        'customers': out,
    }


INSIGHT_FUNCS = {
    'who_to_contact_today': who_to_contact_today,
    'win_back': win_back_candidates,
    'reward_vips': vip_to_reward,
    'grow_rising': rising_customers,
}


def best_send_window():
    """Aggregate predicted send hours into a recommended outreach window."""
    rows = (
        Customer.objects.filter(total_orders__gt=0)
        .values('predicted_send_hour')
        .annotate(n=Count('id'))
        .order_by('-n')
    )
    rows = list(rows)
    if not rows:
        return {'recommended_hour': 10, 'distribution': []}
    top = rows[0]['predicted_send_hour']
    return {
        'recommended_hour': top,
        'distribution': [{'hour': r['predicted_send_hour'], 'customers': r['n']} for r in rows[:6]],
    }
