from datetime import timedelta
from django.db.models import Q
from django.utils import timezone
from apps.customers.models import Customer


SUPPORTED_FIELDS = {
    'total_spend': {'gte', 'lte', 'gt', 'lt', 'eq'},
    'total_orders': {'gte', 'lte', 'gt', 'lt', 'eq'},
    'last_order_at': {'days_ago_gte', 'days_ago_lte'},
    'rfm_recency_score': {'gte', 'lte', 'eq'},
    'rfm_frequency_score': {'gte', 'lte', 'eq'},
    'rfm_monetary_score': {'gte', 'lte', 'eq'},
    'rfm_composite': {'gte', 'lte'},
    'rfm_tier': {'eq', 'in'},
    'churn_risk_score': {'gte', 'lte'},
    'city': {'eq', 'in'},
    'gender': {'eq', 'in'},
    'channel_preference': {'eq', 'in'},
    'tags': {'contains', 'contains_any'},
    'created_at': {'days_ago_gte', 'days_ago_lte'},
}

ORM_OP_SUFFIX = {
    'gte': '__gte', 'lte': '__lte', 'gt': '__gt', 'lt': '__lt', 'eq': '',
    'in': '__in',
}


class SegmentEvaluator:
    def evaluate(self, filter_tree: dict):
        if not filter_tree:
            return Customer.objects.all()
        q = self._build_q(filter_tree)
        return Customer.objects.filter(q).distinct()

    def _build_q(self, node: dict) -> Q:
        if 'conditions' in node:
            op = node.get('operator', 'AND').upper()
            sub_qs = [self._build_q(c) for c in node['conditions']]
            if not sub_qs:
                return Q()
            result = sub_qs[0]
            for sq in sub_qs[1:]:
                result = result & sq if op == 'AND' else result | sq
            return result
        return self._leaf_to_q(node)

    def _leaf_to_q(self, leaf: dict) -> Q:
        field = leaf.get('field')
        op = leaf.get('op')
        value = leaf.get('value')
        if field not in SUPPORTED_FIELDS:
            raise ValueError(f"Unsupported field: {field}")
        if op not in SUPPORTED_FIELDS[field]:
            raise ValueError(f"Unsupported op '{op}' for field '{field}'")

        # Date fields
        if op == 'days_ago_lte':
            cutoff = timezone.now() - timedelta(days=int(value))
            return Q(**{f'{field}__gte': cutoff})
        if op == 'days_ago_gte':
            cutoff = timezone.now() - timedelta(days=int(value))
            return Q(**{f'{field}__lte': cutoff}) | Q(**{f'{field}__isnull': True})

        # Tag ops on ArrayField
        if field == 'tags':
            if op == 'contains':
                return Q(tags__contains=[value])
            if op == 'contains_any':
                vals = value if isinstance(value, list) else [value]
                return Q(tags__overlap=vals)

        suffix = ORM_OP_SUFFIX[op]
        return Q(**{f'{field}{suffix}': value})
