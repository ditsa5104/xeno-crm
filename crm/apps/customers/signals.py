from decimal import Decimal
from django.db.models import Sum, Count, Max
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Order, Customer


def _recompute_customer_stats(customer_id):
    agg = Order.objects.filter(
        customer_id=customer_id,
        status__in=['placed', 'fulfilled'],
    ).aggregate(
        total_orders=Count('id'),
        total_spend=Sum('total_amount'),
        last_order_at=Max('ordered_at'),
    )
    Customer.objects.filter(id=customer_id).update(
        total_orders=agg['total_orders'] or 0,
        total_spend=agg['total_spend'] or Decimal('0'),
        last_order_at=agg['last_order_at'],
    )


@receiver(post_save, sender=Order)
def order_saved(sender, instance, **kwargs):
    _recompute_customer_stats(instance.customer_id)


@receiver(post_delete, sender=Order)
def order_deleted(sender, instance, **kwargs):
    _recompute_customer_stats(instance.customer_id)
