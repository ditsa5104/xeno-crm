from collections import Counter
from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
from django.db.models import F
from .models import Customer


class RFMScorer:
    RFM_TIERS = {
        (4, 4): 'Champions',
        (5, 5): 'Champions',
        (5, 4): 'Champions',
        (4, 5): 'Champions',
        (4, 3): 'Loyal',
        (3, 4): 'Loyal',
        (5, 3): 'Loyal',
        (3, 5): 'Loyal',
        (3, 3): 'Potential Loyalists',
        (4, 1): 'Recent Customers',
        (4, 2): 'Recent Customers',
        (5, 1): 'Recent Customers',
        (5, 2): 'Recent Customers',
        (2, 3): 'At Risk',
        (2, 4): 'At Risk',
        (2, 5): 'At Risk',
        (1, 1): 'Lost',
        (1, 2): 'About to Lose',
    }

    @staticmethod
    def _quintile_rank(values: list[float], reverse: bool = False) -> dict:
        """Return mapping value -> 1..5 score. reverse=True means lower=better (recency)."""
        if not values:
            return {}
        sorted_vals = sorted(values, reverse=reverse)
        n = len(sorted_vals)
        ranks = {}
        for i, v in enumerate(sorted_vals):
            quintile = min(5, (i * 5) // n + 1)
            ranks[v] = quintile
        return ranks

    def compute_all(self):
        now = timezone.now()
        customers = list(Customer.objects.filter(total_orders__gt=0))
        if not customers:
            return 0

        recency_days = []
        freq = []
        monetary = []
        for c in customers:
            days = (now - c.last_order_at).days if c.last_order_at else 9999
            recency_days.append(days)
            freq.append(c.total_orders)
            monetary.append(float(c.total_spend))

        r_rank = self._quintile_rank(recency_days, reverse=True)
        f_rank = self._quintile_rank(freq, reverse=False)
        m_rank = self._quintile_rank(monetary, reverse=False)

        for c, rd, fv, mv in zip(customers, recency_days, freq, monetary):
            r = r_rank.get(rd, 1)
            f = f_rank.get(fv, 1)
            m = m_rank.get(mv, 1)
            composite = r * 0.3 + f * 0.3 + m * 0.4
            tier = self.RFM_TIERS.get((r, f), 'Others')
            c.rfm_recency_score = r
            c.rfm_frequency_score = f
            c.rfm_monetary_score = m
            c.rfm_composite = round(composite, 3)
            c.rfm_tier = tier
            c.churn_risk_score = self.compute_churn_risk(c)
            c.predicted_send_hour = self.compute_predicted_send_hour(c)
            c.ltv_estimate = self.compute_ltv(c)

        Customer.objects.bulk_update(
            customers,
            [
                'rfm_recency_score', 'rfm_frequency_score', 'rfm_monetary_score',
                'rfm_composite', 'rfm_tier', 'churn_risk_score',
                'predicted_send_hour', 'ltv_estimate',
            ],
            batch_size=500,
        )
        return len(customers)

    def compute_churn_risk(self, customer: Customer) -> float:
        if not customer.last_order_at:
            return 1.0
        days = (timezone.now() - customer.last_order_at).days
        score = days / 365.0
        if customer.rfm_frequency_score < 2:
            score += 0.1
        if customer.rfm_composite > 4:
            score -= 0.15
        return max(0.0, min(1.0, round(score, 3)))

    def compute_predicted_send_hour(self, customer: Customer) -> int:
        hours = list(customer.orders.values_list('ordered_at', flat=True))
        if not hours:
            return 10
        c = Counter(h.hour for h in hours if h)
        if not c:
            return 10
        return c.most_common(1)[0][0]

    def compute_ltv(self, customer: Customer) -> Decimal:
        if customer.total_orders == 0:
            return Decimal('0')
        avg = float(customer.total_spend) / customer.total_orders
        age_days = (timezone.now() - customer.created_at).days if customer.created_at else 30
        age_years = max(age_days / 365.0, 0.5)
        ltv = avg * (customer.total_orders / age_years) * 2
        return Decimal(str(round(min(ltv, 500000.0), 2)))
