from django.contrib import admin
from .models import Customer, Order


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'city', 'rfm_tier', 'total_spend', 'total_orders', 'last_order_at')
    list_filter = ('rfm_tier', 'gender', 'channel_preference', 'city')
    search_fields = ('name', 'email', 'phone', 'external_id')
    readonly_fields = (
        'rfm_recency_score', 'rfm_frequency_score', 'rfm_monetary_score',
        'rfm_composite', 'rfm_tier', 'churn_risk_score',
        'predicted_send_hour', 'ltv_estimate',
        'last_order_at', 'total_orders', 'total_spend',
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'total_amount', 'status', 'channel', 'ordered_at')
    list_filter = ('status', 'channel')
    search_fields = ('order_number', 'customer__name', 'customer__email')
